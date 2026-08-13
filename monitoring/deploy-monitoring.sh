#!/usr/bin/env bash
#
# deploy-monitoring.sh — push this repo's monitoring config into the running
# Prometheus/Alertmanager/Grafana stack. Run it on the VPS:
#
#   ~/pe-portfolio/monitoring/deploy-monitoring.sh
#
# The stack itself is vegasbrianc/prometheus cloned at ~/prometheus. Only the
# config files below are ours; keeping them here means they are reviewed and
# versioned with the site instead of edited in place on the server.
#
# The new config is validated with promtool/amtool before anything is
# reloaded, and the previous copy is restored if validation fails.

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="${STACK_DIR:-$HOME/prometheus}"
WEBHOOK_FILE="$STACK_DIR/alertmanager/discord_webhook_url"

FILES=(
  "prometheus/prometheus.yml"
  "prometheus/alert.rules"
  "alertmanager/config.yml"
  "grafana/provisioning/datasources/datasource.yml"
  "grafana/provisioning/dashboards/portfolio-overview.json"
)

[ -d "$STACK_DIR" ] || { echo "No monitoring stack at $STACK_DIR" >&2; exit 1; }

BACKUP_DIR="$(mktemp -d -t monitoring-backup.XXXXXX)"
restore() {
  echo "Restoring the previous config from $BACKUP_DIR"
  for file in "${FILES[@]}"; do
    [ -f "$BACKUP_DIR/$file" ] && cp "$BACKUP_DIR/$file" "$STACK_DIR/$file"
  done
}

echo "==> Backing up current config to $BACKUP_DIR"
for file in "${FILES[@]}"; do
  if [ -f "$STACK_DIR/$file" ]; then
    mkdir -p "$BACKUP_DIR/$(dirname "$file")"
    cp "$STACK_DIR/$file" "$BACKUP_DIR/$file"
  fi
done

echo "==> Copying config from $SOURCE_DIR"
for file in "${FILES[@]}"; do
  mkdir -p "$STACK_DIR/$(dirname "$file")"
  cp "$SOURCE_DIR/$file" "$STACK_DIR/$file"
  echo "    $file"
done

if [ ! -s "$WEBHOOK_FILE" ]; then
  cat >&2 <<EOF

The Discord webhook URL is missing. Alertmanager will start but every
notification will fail. Create it with:

  printf '%s' 'https://discord.com/api/webhooks/...' > $WEBHOOK_FILE
  chmod 600 $WEBHOOK_FILE

EOF
  exit 1
fi

echo "==> Validating"
if ! docker exec prometheus-prometheus-1 promtool check config /etc/prometheus/prometheus.yml; then
  restore
  exit 1
fi
if ! docker exec prometheus-alertmanager-1 amtool check-config /etc/alertmanager/config.yml; then
  restore
  exit 1
fi

# Prometheus and Alertmanager both reload their config on SIGHUP, which avoids
# a restart (and the gap in scraped data that comes with one). Grafana only
# reads provisioned datasources at startup, so it does get restarted.
echo "==> Reloading"
docker kill -s HUP prometheus-prometheus-1 prometheus-alertmanager-1
docker restart prometheus-grafana-1 >/dev/null
echo "    prometheus and alertmanager reloaded, grafana restarted"

echo
echo "Prometheus rules:  http://167.172.138.95:9090/rules"
echo "Alertmanager:      http://167.172.138.95:9093"
echo "Grafana dashboard: http://167.172.138.95:3000/d/portfolio-overview"
