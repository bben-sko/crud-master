#!/bin/bash

apt-get install -y postgresql postgresql-contrib postgresql-client libpq-dev
sudo -u postgres psql -c "CREATE DATABASE billing_db;"
sudo -u postgres psql -c "CREATE USER billing_user WITH PASSWORD 'billingpass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE billing_db TO billing_user;"

apt-get install -y rabbitmq-server
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
rabbitmq-plugins enable rabbitmq_management

curl -fsSL https://deb.nodesource.com/setup_20.x | bash
sudo apt-get install -y nodejs
sudo npm install -g pm2


cd billing-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


sudo pm2 start server.py --interpreter venv/bin/python3 --name billing-app
sudo pm2 save
sudo pm2 startup