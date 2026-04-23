#!/usr/bin/env bash
set -e

APP_DIR="${BILLING_APP_DIR:-/home/vagrant/billing-app}"
APP_NAME="billing-consumer"

export DEBIAN_FRONTEND=noninteractive

apt-get install -y postgresql postgresql-client postgresql-contrib libpq-dev rabbitmq-server
systemctl enable postgresql
systemctl start postgresql
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
rabbitmq-plugins enable rabbitmq_management

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${BILLING_DB_USER}'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE USER ${BILLING_DB_USER} WITH PASSWORD '${BILLING_DB_PASSWORD}';"
else
  sudo -u postgres psql -c "ALTER USER ${BILLING_DB_USER} WITH PASSWORD '${BILLING_DB_PASSWORD}';"
fi

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${BILLING_DB_NAME}'" | grep -q 1; then
  sudo -u postgres createdb "${BILLING_DB_NAME}" -O "${BILLING_DB_USER}"
fi

sudo -u postgres psql -c "ALTER DATABASE ${BILLING_DB_NAME} OWNER TO ${BILLING_DB_USER};"
sudo -u postgres psql -d "${BILLING_DB_NAME}" -c "GRANT ALL ON SCHEMA public TO ${BILLING_DB_USER};"

if ! rabbitmqctl list_users | awk '{print $1}' | grep -qx "${RABBITMQ_USER}"; then
  rabbitmqctl add_user "${RABBITMQ_USER}" "${RABBITMQ_PASSWORD}"
else
  rabbitmqctl change_password "${RABBITMQ_USER}" "${RABBITMQ_PASSWORD}"
fi

rabbitmqctl set_user_tags "${RABBITMQ_USER}" administrator
rabbitmqctl set_permissions -p / "${RABBITMQ_USER}" ".*" ".*" ".*"

cd "$APP_DIR"

python3 -m venv venv
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r requirements.txt

cat > "$APP_DIR/.env" <<EOF
BILLING_DB_HOST=${BILLING_DB_HOST}
BILLING_DB_PORT=${BILLING_DB_PORT}
BILLING_DB_NAME=${BILLING_DB_NAME}
BILLING_DB_USER=${BILLING_DB_USER}
BILLING_DB_PASSWORD=${BILLING_DB_PASSWORD}
BILLING_DB_URL=postgresql://${BILLING_DB_USER}:${BILLING_DB_PASSWORD}@${BILLING_DB_HOST}:${BILLING_DB_PORT}/${BILLING_DB_NAME}
RABBITMQ_HOST=localhost
RABBITMQ_PORT=${RABBITMQ_PORT}
RABBITMQ_USER=${RABBITMQ_USER}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
RABBITMQ_QUEUE=${RABBITMQ_QUEUE}
BILLING_RETRY_DELAY=${BILLING_RETRY_DELAY}
EOF

if sudo pm2 describe "$APP_NAME" >/dev/null 2>&1; then
  sudo pm2 delete "$APP_NAME"
fi

sudo pm2 start "$APP_DIR/server.py" \
  --name "$APP_NAME" \
  --cwd "$APP_DIR" \
  --interpreter "$APP_DIR/venv/bin/python"
sudo pm2 save
