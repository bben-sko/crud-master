#!/bin/bash

#install nodejs and npm
curl -fsSL https://deb.nodesource.com/setup_20.x | bash
sudo apt-get install -y nodejs
sudo npm install -g npm@latest
sudo npm install -g pm2

#setup python venv and install dependencies
# ─── Setup Python venv ────────────────────────────────────────────
echo "[3/4] Setting up Python environment..."
cd /vagrant/srcs/api-gateway-app
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# ─── Start app with PM2 ───────────────────────────────────────────
echo "[4/4] Starting API Gateway with PM2..."
pm2 start /vagrant/srcs/api-gateway-app/server.py \
    --interpreter /vagrant/srcs/api-gateway-app/venv/bin/python3 \
    --name api-gateway \
    --cwd /vagrant/srcs/api-gateway-app
pm2 save