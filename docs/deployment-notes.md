# Deployment Notes

Project dir:
```
cd "/mnt/c/Users/huzai/Desktop/GitHub Projects/pe-portfolio"
```

## SSH into VPS
```
ssh -i ~/.ssh/id_ed25519 root@167.172.138.95
```

## Start Flask
```
cd pe-portfolio
source venv/bin/activate
flask run --host=0.0.0.0
```

## Start Flask in background (stays running after you disconnect)
```
cd pe-portfolio
source venv/bin/activate
nohup flask run --host=0.0.0.0 &
```

## Check if Flask is running
```
ps aux | grep flask
```

## Stop Flask (background)
```
pkill -f flask
```

## Site URL
http://huzaifa-pe-portfolio.duckdns.org:5000
