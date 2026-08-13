#!/usr/bin/env bash
#
# load-test.sh — drive traffic at the portfolio site so every container in the
# stack does measurable work while you watch Grafana.
#
# The request mix deliberately covers all three containers:
#   /                     nginx + Flask (template rendering)
#   /hobbies /timeline    nginx + Flask
#   /api/timeline_post    nginx + Flask + MariaDB (SELECT)
#   /health               nginx + Flask + MariaDB + nginx stub_status
#
# Usage:
#   ./load-test.sh [seconds] [concurrency]
#   BASE_URL=http://localhost:5000 ./load-test.sh 60 10
#
# Requires: curl and awk. Nothing to install on the VPS.

set -uo pipefail

BASE_URL="${BASE_URL:-https://huzaifa-pe-portfolio.duckdns.org}"
DURATION="${1:-120}"
CONCURRENCY="${2:-20}"

PATHS=(
  "/"
  "/health"
  "/api/timeline_post"
  "/timeline"
  "/hobbies"
  "/health"
)

RESULTS="$(mktemp -t load-test.XXXXXX)"
PIDS=()

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null
  done
  wait 2>/dev/null
}
trap cleanup EXIT INT TERM

worker() {
  local deadline="$1"
  while [ "$(date +%s)" -lt "$deadline" ]; do
    for path in "${PATHS[@]}"; do
      # One line per request: path, status code, seconds.
      curl -s -o /dev/null -m 10 \
        -w "$path %{http_code} %{time_total}\n" \
        "$BASE_URL$path" >>"$RESULTS" 2>/dev/null \
        || echo "$path 000 0" >>"$RESULTS"
    done
  done
}

echo "Load test"
echo "  target:      $BASE_URL"
echo "  duration:    ${DURATION}s"
echo "  concurrency: $CONCURRENCY workers"
echo "  paths:       ${PATHS[*]}"
echo
echo "Watch it land in Grafana: http://167.172.138.95:3000 (Portfolio Site Overview)"
echo

STARTED="$(date +%s)"
DEADLINE=$((STARTED + DURATION))

for _ in $(seq 1 "$CONCURRENCY"); do
  worker "$DEADLINE" &
  PIDS+=("$!")
done

wait "${PIDS[@]}" 2>/dev/null
ELAPSED=$(($(date +%s) - STARTED))
[ "$ELAPSED" -gt 0 ] || ELAPSED=1

echo "--- results -----------------------------------------------------------"
awk -v elapsed="$ELAPSED" '
  {
    total++
    latency[$1] += $3
    count[$1]++
    status[$2]++
    if ($3 > slowest[$1]) slowest[$1] = $3
  }
  END {
    printf "%d requests in %ds (%.1f req/s)\n\n", total, elapsed, total / elapsed

    # Each section is piped through sort so the rows come out in a stable
    # order; fflush keeps the headers ahead of the sorted output.
    printf "%-22s %8s %12s %12s\n", "PATH", "REQUESTS", "AVG", "SLOWEST"
    fflush()
    for (p in count)
      printf "%-22s %8d %10.0f ms %10.0f ms\n", p, count[p], \
        (latency[p] / count[p]) * 1000, slowest[p] * 1000 | "sort"
    close("sort")

    printf "\n%-22s %8s\n", "STATUS", "COUNT"
    fflush()
    for (s in status)
      printf "%-22s %8d\n", (s == "000" ? "000 (no response)" : s), status[s] | "sort"
    close("sort")
  }
' "$RESULTS"

rm -f "$RESULTS"
