#!/bin/bash

apt-get install -y postgresql postgresql-contrib postgresql-client libpq-dev

sudo -u postgres psql -c "CREATE DATABASE inventory_db;"
sudo -u postgres psql -c "CREATE USER inventory_user WITH PASSWORD 'inventorypass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;"


curl -fsSL https://deb.nodesource.com/setup_20.x | bash
sudo apt-get install -y nodejs
sudo npm install -g pm2


cd inventory-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo pm2 start server.py --interpreter venv/bin/python3 --name billing-app
sudo pm2 save
sudo pm2 startup