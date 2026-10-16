# Demo video script (record in this exact order — M10 requirement)

Total ~10-14 min. Record at 1080p, mic on, terminal font ≥16pt.

1. **Slides (0:00-2:30)** — open `demo/slides.pdf`: what MediDesk is, tech stack,
   architecture diagram, CI/CD flow, infra, K8s, observability, learnings.
2. **Codebase (2:30-4:00)** — `tree` / VS Code: `backend/app`, `alembic/versions`,
   `frontend/src`, `docker-compose.yml`, `terraform/`, `helm/medidesk`, `monitoring/`.
   Open `routes.py`, `ci.yml`, `main.tf`.
3. **CI/CD (4:00-6:00)** — `git commit -m "feat: ..."` + `git push origin main`,
   open the Actions run, show test → build → Trivy → push steps going green, then
   GHCR package page with the new SHA tag.
4. **Terraform (6:00-7:30)** — `terraform plan` output, `terraform apply` tail,
   AWS Console: VPC (subnets) + EKS cluster + node group in ap-south-1.
5. **ArgoCD (7:30-8:30)** — dashboard: `medidesk` app Synced/Healthy, show
   auto-sync after a values change + `kubectl get pods -n medidesk` rolling update.
6. **Kubernetes (8:30-10:00)** — `kubectl get pods,svc,ingress,hpa -n medidesk`
   all Running, `helm list -n medidesk`, open app via Ingress host/ALB IP, create
   an appointment live, show `kubectl describe` on a troubleshooting pod if asked.
7. **Prometheus (10:00-11:00)** — `curl <backend>/metrics | head`, Targets page
   with `medidesk/backend` UP.
8. **Grafana (11:00-12:00)** — dashboard: request rate + p95 latency + error rate
   moving while you click the app / run `scripts/load-test.sh`.
9. **Close** — `terraform destroy` note (cost), recap.

Save export as `demo/presentation.mp4` (≤500MB for GitHub web; else Git LFS /
release asset + link in README). Missing video = 0/5 for M10.
