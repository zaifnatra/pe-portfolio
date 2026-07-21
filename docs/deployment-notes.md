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

## Redeploy the site (after pushing changes to GitHub)
```
~/redeploy-site.sh
```
This pulls `origin/main`, then `docker compose -f docker-compose.prod.yml down` and `up -d --build`.

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
