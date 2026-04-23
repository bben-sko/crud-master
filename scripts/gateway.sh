#!/bin/bash

#install nodejs and npm
curl -fsSL https://deb.nodesource.com/setup_20.x | bash
sudo apt-get install -y nodejs
sudo npm install -g npm@latest
sudo npm install -g pm2

#setup python venv and install dependencies
cd api-gateway-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt