# Deployment Notes

The site now runs in Docker (Flask + MariaDB containers) via docker-compose.

Local project dir:
```
cd "/mnt/c/Users/huzai/Desktop/GitHub Projects/pe-portfolio"
```

Site URL: https://huzaifa-pe-portfolio.duckdns.org

Traffic now goes through an `nginx` (jonasal/nginx-certbot) container that terminates
HTTPS and reverse-proxies to the `myportfolio` (Flask) container over HTTP. The Flask
container no longer publishes port 5000 to the host — only nginx binds 80/443.
Nginx config: `user_conf.d/myportfolio.conf`.

## SSH into VPS
```
ssh -i ~/.ssh/id_ed25519 root@167.172.138.95
```
The VPS runs CentOS/RHEL: use `dnf` (not `apt`), `firewalld` (not `ufw`), and there is no `nano` by default (`vi`, or `dnf install -y nano`).

## Redeploy the site

Pushing to `main` deploys automatically via `.github/workflows/deploy.yml`.
The same workflow can be triggered by hand from the Actions tab ("Run workflow").

The workflow runs three jobs:

1. `test` - calls `.github/workflows/test.yml` as a reusable workflow. `test.yml` itself only triggers on
   pull requests, so a push to `main` produces one combined run rather than a duplicate test run.
2. `deploy` - needs `test`, so a failing test suite blocks the deploy. It SSHes in, runs `~/redeploy-site.sh`,
   prints `docker compose -f docker-compose.prod.yml ps` into the run log, then posts a success message to Discord.
3. `notify-failure` - `if: failure()`, so it fires whether the tests or the deploy broke, and says which.

To redeploy manually on the VPS instead:
```
~/redeploy-site.sh
```
This pulls `origin/main`, then `docker compose -f docker-compose.prod.yml down` and `up -d --build`.
The script hardcodes `$HOME/pe-portfolio`, so the workflow needs no project-path secret.

The workflow authenticates with the `github-actions-vps` key, whose public half is in `/root/.ssh/authorized_keys`.
Its private half is the `SSH_PRIVATE_KEY` repo secret, alongside `SSH_IP` and `SSH_USER`.
Because this key is separate from the personal `id_ed25519` login key, it can be revoked (drop its line from
`authorized_keys`) without locking yourself out of the VPS.

## Discord notifications

Both notification steps go through `.github/scripts/discord-notify.sh`, which posts to the `DISCORD_WEBHOOK`
repo secret (a webhook created under Channel Settings > Integrations > Webhooks; the URL starts with
`https://discord.com/api/webhooks/`). Every message carries the short commit SHA and a link back to the run log.

The script fails loudly if `DISCORD_WEBHOOK` is unset or the POST is rejected, rather than silently sending nothing.

## Manual container commands (on the VPS)
```
cd ~/pe-portfolio

# start / rebuild
docker compose -f docker-compose.prod.yml up -d --build

# status
docker compose -f docker-compose.prod.yml ps

# logs (follow)
docker compose -f docker-compose.prod.yml logs -f

# stop
docker compose -f docker-compose.prod.yml down
```

## Config (VPS `.env`, not in git)
```
MYSQL_HOST=mysql            # points at the mysql container, not localhost
MYSQL_USER=myportfolio
MYSQL_PASSWORD=mypassword
MYSQL_DATABASE=myportfoliodb   # mariadb image needs this exact key to auto-create the DB
MYSQL_ROOT_PASSWORD=myrootpassword
```
Data lives in the named volume `mydatabase` and persists across reboots/rebuilds.

## Gotchas
- On first `up`, expect ~15-20s of `Can't connect to MySQL server 'mysql' ([Errno 111] Connection refused)`
  in the `myportfolio` logs while MariaDB initializes. `restart: always` retries until it connects — this is normal.
- If the site works via `curl` on the VPS but not in a browser, open the ports in firewalld.
  With nginx you need 80 and 443 (port 5000 is no longer published to the host):
  ```
  firewall-cmd --permanent --add-port=80/tcp --add-port=443/tcp && firewall-cmd --reload
  ```
- Certbot needs port 80 reachable from the internet to issue the certificate. Watch
  `docker compose -f docker-compose.prod.yml logs -f nginx` on first boot for cert issuance.
- Changing `MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE` after the volume exists won't take effect
  unless you remove the volume (`docker volume rm pe-portfolio_mydatabase`) — this wipes all data.

## Quick health check
Port 5000 is no longer published to the host, so hit it through nginx instead:
```
curl -k https://localhost/api/timeline_post          # on the VPS
curl https://huzaifa-pe-portfolio.duckdns.org/api/timeline_post
```
