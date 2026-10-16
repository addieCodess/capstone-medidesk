# Trivy security scan — what it does

Trivy (`aquasecurity/trivy-action@0.30.0` in `.github/workflows/ci.yml`) scans both
`medidesk-backend` and `medidesk-frontend` images for OS + library CVEs at
`HIGH,CRITICAL` severity with `ignore-unfixed: true` and `exit-code: 1`.

- Clean run prints `Total: 0 (HIGH: 0, CRITICAL: 0)` per target: no known fixable
  HIGH/CRITICAL vulns found; the pipeline passes and pushes the SHA-tagged images.
- If e.g. `CVE-2024-4741 (openssl, HIGH)` appears, the job exits 1, nothing is
  pushed/deployed. Fix: bump the base image (`python:3.12-slim`, `nginx-unprivileged`)
  or the affected package, rebuild, re-scan until green.
- Screenshots for submission: the two "Scan backend/frontend" steps in a green
  Actions run, plus `docker build` + `trivy image` local output if desired.
