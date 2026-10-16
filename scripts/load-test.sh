#!/usr/bin/env bash
# Simple load generator for HPA demo: kubectl get hpa -n medidesk -w in another terminal.
set -e
URL="${1:-http://localhost:8000/api/appointments}"
N="${2:-500}"
for i in $(seq 1 "$N"); do
  curl -s "$URL" > /dev/null &
  if [ $((i % 50)) -eq 0 ]; then wait; echo "sent $i"; fi
done
wait
echo done
