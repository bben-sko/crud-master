#!/bin/bash

apt-get install -y postgresql postgresql-contrib postgresql-client libpq-dev
apt-get install -y rabbitmq-server
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
rabbitmq-plugins enable rabbitmq_management