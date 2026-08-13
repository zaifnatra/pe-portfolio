# Monitoring Notes

Prometheus, Grafana, Alertmanager, cAdvisor and node-exporter run on the same VPS as the site, from a clone of [vegasbrianc/prometheus](https://github.com/vegasbrianc/prometheus) at `~/prometheus`.

That clone is upstream code.
Everything in this repo's [monitoring/](../monitoring/) directory is ours, and `monitoring/deploy-monitoring.sh` copies it into the stack.
Editing the config on the server directly means the next `git pull` in `~/prometheus` silently reverts it, so don't.

| URL | What |
| --- | --- |
| http://167.172.138.95:3000 | Grafana (`admin` / see `~/prometheus/grafana/config.monitoring`) |
| http://167.172.138.95:3000/d/portfolio-overview | The custom dashboard |
| http://167.172.138.95:9090 | Prometheus |
| http://167.172.138.95:9090/rules | Alert rules and their current state |
| http://167.172.138.95:9093 | Alertmanager (silence alerts here) |
| http://167.172.138.95:8080 | cAdvisor |

## How the site is monitored

The Flask app serves two operational endpoints, neither of which appears in the nav bar.

`/health` runs one check per dependency and returns `200` when they all pass, `503` when any fail:

```json
{
  "status": "ok",
  "served_by": "2b347568b26b",
  "checks": {
    "database": { "status": "ok", "timeline_posts": 3, "latency_ms": 1.84 },
    "nginx": { "status": "ok", "active_connections": 1, "latency_ms": 0.92 }
  },
  "duration_ms": 2.83
}
```

The database check runs a real `SELECT`, and the nginx check reads `stub_status` from an internal-only server on port 8080 (see `user_conf.d/myportfolio.conf`), which is never published to the host.
So a request to `/health` touches nginx, Flask and MariaDB in one go — which is the point.
During the load-testing exercise MariaDB sat idle, because nothing on the pages being hammered actually queried it.

`/metrics` serves Prometheus request counts, latency histograms and status codes.
It also re-runs the health checks on every scrape and exposes them as `portfolio_dependency_up` and `portfolio_dependency_check_duration_seconds`, which means:

- the dependency alerts work without anyone ever calling `/health` by hand, and
- MariaDB and nginx see steady traffic every 15s instead of showing a flat line.

Prometheus scrapes the app over the `prometheus_back-tier` docker network, so `/metrics` never has to be exposed publicly — nginx returns 404 for it.
That network is declared `external` in `docker-compose.prod.yml`: **the monitoring stack has to be up before the site stack**, or `docker compose up` fails with "network not found".

## Deploying config changes

```bash
ssh -i ~/.ssh/github-actions-vps root@167.172.138.95
cd ~/pe-portfolio && git pull
./monitoring/deploy-monitoring.sh
```

The script backs up the current config, copies ours in, validates it with `promtool check config` and `amtool check-config`, and only then reloads.
If validation fails it puts the backup back.
Prometheus and Alertmanager reload on `SIGHUP` (no restart, no gap in the graphs); Grafana is restarted because it only reads provisioned datasources at startup.

## Alerts

Rules live in [monitoring/prometheus/alert.rules](../monitoring/prometheus/alert.rules), grouped by what they watch: availability, traffic, containers, host, and the monitoring stack itself.
Thresholds are set for this box specifically — 2 vCPU, 1.7 GB RAM, 60 GB disk, no swap.

Two severities, both going to the same Discord channel:

| Severity | Examples | Wait before firing | Repeat |
| --- | --- | --- | --- |
| `critical` | site down, a dependency failing, a container gone, disk nearly full | 10s | hourly |
| `warning` | high CPU/memory/load, slow responses, 5xx rate, container restarted | 30s | every 4h |

Inhibition rules keep one failure from producing five messages: a critical alert suppresses warnings for the same alert and instance, and `PortfolioSiteDown` suppresses the dependency, latency and `TargetDown` alerts that follow from it.

### The Discord webhook

Alertmanager reads the webhook URL from `/etc/alertmanager/discord_webhook_url`, which is `~/prometheus/alertmanager/discord_webhook_url` on the host.
It is a secret, so it is **not** in git — `discord_webhook_url` is in `.gitignore`.

To rotate it (Discord → Channel Settings → Integrations → Webhooks):

```bash
printf '%s' 'https://discord.com/api/webhooks/...' > ~/prometheus/alertmanager/discord_webhook_url
chmod 600 ~/prometheus/alertmanager/discord_webhook_url
docker kill -s HUP prometheus-alertmanager-1
```

If notifications stop arriving, `AlertmanagerNotificationsFailing` fires on the stack's own metrics — but that alert has to reach Discord too, so check http://167.172.138.95:9093 and `docker logs prometheus-alertmanager-1` when things go quiet.

### Firing a test alert

Stopping MariaDB is the cleanest end-to-end test, since it exercises the health checks, the rules and the notification path at once:

```bash
docker stop mysql
# ~2 min later: PortfolioDependencyDown (critical) in Discord, and
# curl -s -o /dev/null -w '%{http_code}\n' https://huzaifa-pe-portfolio.duckdns.org/health  ->  503
docker start mysql
# the resolved message follows within ~5 min
```

To send a message without breaking anything, post a synthetic alert straight to Alertmanager:

```bash
curl -X POST http://localhost:9093/api/v2/alerts -H 'Content-Type: application/json' -d '[{
  "labels": {"alertname": "TestAlert", "severity": "critical", "instance": "manual"},
  "annotations": {"summary": "Test alert", "description": "Checking the Discord webhook."}
}]'
```

## Load testing

```bash
~/pe-portfolio/monitoring/load-test.sh 120 20     # 120s, 20 concurrent workers
BASE_URL=http://localhost:5000 ./monitoring/load-test.sh 60 10
```

It cycles through `/`, `/timeline`, `/hobbies`, `/api/timeline_post` and `/health`, so nginx, Flask and MariaDB all move on the dashboard, and prints a per-path latency and status-code summary at the end.
20 workers is enough to make the graphs interesting on a 2-core box; well past that you are mostly measuring the load generator.

`~/monitoring-with-cli/test1.py` and `test2` are the CPU burners from the earlier exercise — useful for making the host CPU and load alerts fire.

## Dashboard

[monitoring/grafana/provisioning/dashboards/portfolio-overview.json](../monitoring/grafana/provisioning/dashboards/portfolio-overview.json), provisioned from disk, so edits made in the Grafana UI are lost on the next restart.
To keep a change, export it (Dashboard settings → JSON Model), save it over that file, commit, and redeploy.

Top row answers "is it alright" at a glance: site up, dependencies healthy, request rate, p95, error rate, alerts firing.
Below that, traffic by path and status code, latency percentiles, and the dependency check timings; then per-container CPU, memory and network from cAdvisor, and host CPU/memory/disk from node-exporter.
Alerts that fire are drawn as red annotations across the time axis, so a spike lines up with whatever paged.
