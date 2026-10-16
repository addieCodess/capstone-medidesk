# MediDesk — Clinic Appointment & Care Task Manager (DevSecOps Capstone)

MediDesk is a SaaS-style clinic appointment manager built for the DevSecOps capstone.
Own application domain (not a TaskBoard clone): schedule, check-in, track and cancel
patient appointments with priorities and per-status stats.

## Architecture

```
Developer → Git/GitHub → GitHub Actions (pytest → build → Trivy → push GHCR w/ SHA)
  → Terraform (VPC + EKS, ap-south-1) → Helm release (medidesk ns)
  → Frontend (React) + Backend (FastAPI) + PostgreSQL (in-cluster PVC for demo; RDS for prod)
  → Ingress (/ → frontend, /api → backend) → HPA (CPU)
  → Prometheus (ServiceMonitor scrapes /metrics) → Grafana dashboard
  → ArgoCD Application (GitOps sync from helm/medidesk)
```

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, psycopg 3, prometheus-fastapi-instrumentator |
| Frontend | React 18 + Vite, Nginx unprivileged runtime |
| DB | PostgreSQL 16 (compose + in-cluster; RDS recommended for prod) |
| Tests | pytest 8, httpx TestClient, SQLite test DB (`conftest.py`) |
| Containers | Docker, multi-stage frontend, non-root users both images |
| CI/CD | GitHub Actions (test → build-scan-push → deploy), GHCR with `${{ github.sha }}` tags |
| Security | Trivy HIGH/CRITICAL gate (`exit-code: 1`), no secrets in git |
| IaC | Terraform 1.5+, AWS VPC module 5.x + EKS module 20.x, EKS 1.30, `t3.medium` node group |
| GitOps | Helm chart `helm/medidesk` + ArgoCD `k8s/argocd-app.yaml` |
| K8s | Namespace `medidesk`, Deployments ×2 replicas, ClusterIP SVCs, Ingress NGINX, HPA |
| Observability | kube-prometheus-stack, ServiceMonitor, Grafana dashboard JSON |

## Local setup

```bash
docker compose up --build
# frontend http://localhost:3000  backend http://localhost:8000/docs
# health: curl localhost:8000/health | metrics: curl localhost:8000/metrics
docker compose down -v   # also drops DB volume
```

Backend directly:
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://medidesk:medidesk@localhost:5432/medidesk'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Tests: `cd backend && pytest -v` (9 tests, SQLite test DB, never touches prod DB).

## CI/CD pipeline (`.github/workflows/ci.yml`)

1. **test**: checkout → setup Python 3.12 → `pip install -r requirements.txt` → `pytest -q`
   (fails build on test failure) → setup Node 22 → `npm install && npm run build`.
2. **build-scan-push** (needs test): login GHCR → build both images tagged
   `ghcr.io/<owner>/medidesk-backend:${{ github.sha }}` → Trivy scan both
   (`severity: HIGH,CRITICAL`, `ignore-unfixed: true`, `exit-code: 1`) → push both.
3. **deploy** (main only): setup Helm → decode `KUBE_CONFIG_DATA` → 
   `helm upgrade --install medidesk ./helm/medidesk -n medidesk --create-namespace`
   with SHA tags + GHCR image names.

Frontend is built in CI; images carry commit SHA (not `latest`) for traceability.

## Security (Trivy)

Trivy scans both images in CI and fails the pipeline on HIGH/CRITICAL CVEs.
Example clean result: `Total: 0 (HIGH: 0, CRITICAL: 0)` means no known fixable
HIGH/CRITICAL vulns in OS/app layers at scan time — the gate still runs every push.
If a CVE appears (e.g. `CVE-2024-xxxx in libssl`), the job fails, no image is
pushed, and the fix is: bump base image / dependency, rebuild, re-scan.
Required secrets: only `GITHUB_TOKEN` (auto) + `KUBE_CONFIG_DATA` (base64 kubeconfig)
stored as GitHub Actions secret — never committed (see `terraform.tfvars.example`).

## Terraform infrastructure (`terraform/`)

VPC (10.0.0.0/16, 3 AZs, 3 public + 3 private subnets, single NAT) + EKS 1.30
with managed node group (desired 2 × t3.medium, min 1, max 3), public endpoint,
creator admin permissions. Region default `ap-south-1`.

```bash
cd terraform
terraform init
terraform plan    # screenshot for submission
terraform apply   # creates VPC + EKS; then: aws eks update-kubeconfig --region ap-south-1 --name medidesk-eks
terraform destroy # MANDATORY after evaluation to avoid AWS charges
```

## Kubernetes / Helm deployment

```bash
kubectl apply -f k8s/namespace.yaml
helm upgrade --install medidesk ./helm/medidesk -n medidesk --create-namespace
# dev ingress host:
helm upgrade --install medidesk ./helm/medidesk -n medidesk -f helm/medidesk/values-dev.yaml
kubectl get pods,svc,ingress,hpa -n medidesk
helm list -n medidesk
```

2 replicas each for backend/frontend; ClusterIP Services; Ingress routes
`/ → frontend:80`, `/api → backend:8000`; HPA 2–5 pods on 70% CPU.
Postgres runs in-cluster via PVC for demo; production should use RDS
(tradeoff: less ops vs managed backups/HA). ArgoCD: `kubectl apply -f k8s/argocd-app.yaml`
then the dashboard shows Synced/Healthy; every git push to `helm/medidesk` auto-syncs.

Troubleshooting lab: `troubleshooting/broken-image.yaml` (ImagePullBackOff →
`kubectl describe pod`, fix tag) and `broken-service.yaml` (no endpoints →
`kubectl get endpoints`, fix selector labels).

## Observability (Prometheus + Grafana)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml
kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3001:80
# login admin/admin123, import monitoring/grafana-dashboard.json
```

Backend `/metrics` exposes `http_requests_total`, `http_request_duration_seconds_*`.
ServiceMonitor scrapes every 15s; Prometheus Targets shows `medidesk/backend UP`;
dashboard panels: request rate by endpoint, p95 latency, 5xx error rate.
Load test: `bash scripts/load-test.sh http://<backend>:8000/api/appointments 500`
then watch `kubectl get hpa -n medidesk -w` + Grafana.

## API reference

`GET /` `GET /health` `GET /ready` `GET /metrics` `GET /docs`
`GET /api/appointments` `GET /api/appointments/stats` `GET /api/appointments/{id}`
`POST /api/appointments` `PUT /api/appointments/{id}` `DELETE /api/appointments/{id}`

## Known issues / limitations

- In-cluster Postgres is demo-only (no HA/backups); use RDS in prod.
- Ingress needs an NGINX controller + DNS (`medidesk.local` → `/etc/hosts` locally).
- HPA needs metrics-server; low traffic won't scale — use `scripts/load-test.sh`.
- `terraform init` downloads VPC/EKS modules (~minutes, needs network + AWS creds).
- Sandbox here has no Docker Hub/network egress, so `docker build` must run on your machine/CI.

## Submission checklist mapping

M1 app ✅ M2 pytest ✅ M3 git ✅ M4 docker ✅ M5 GH Actions+GHCR+SHA ✅
M6 Trivy ✅ M7 Terraform VPC+EKS ✅ M8 Helm+Ingress+HPA ✅ M9 /metrics+Prom+Grafana ✅
M10 this README + `demo/` (video MP4 + slides) — record per `demo/video-script.md`.
