#!/usr/bin/env bash
set -e

APP_DIR="${INVENTORY_APP_DIR:-/home/vagrant/inventory-app}"
APP_NAME="inventory-api"

export DEBIAN_FRONTEND=noninteractive

apt-get install -y postgresql postgresql-client postgresql-contrib libpq-dev
systemctl enable postgresql
systemctl start postgresql

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${INVENTORY_DB_USER}'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';"
else
  sudo -u postgres psql -c "ALTER USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';"
fi

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${INVENTORY_DB_NAME}'" | grep -q 1; then
  sudo -u postgres createdb "${INVENTORY_DB_NAME}" -O "${INVENTORY_DB_USER}"
fi

sudo -u postgres psql -c "ALTER DATABASE ${INVENTORY_DB_NAME} OWNER TO ${INVENTORY_DB_USER};"
sudo -u postgres psql -d "${INVENTORY_DB_NAME}" -c "GRANT ALL ON SCHEMA public TO ${INVENTORY_DB_USER};"

cd "$APP_DIR"

python3 -m venv venv
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r requirements.txt

cat > "$APP_DIR/.env" <<EOF
INVENTORY_HOST=${INVENTORY_HOST}
INVENTORY_PORT=${INVENTORY_PORT}
INVENTORY_DB_HOST=${INVENTORY_DB_HOST}
INVENTORY_DB_PORT=${INVENTORY_DB_PORT}
INVENTORY_DB_NAME=${INVENTORY_DB_NAME}
INVENTORY_DB_USER=${INVENTORY_DB_USER}
INVENTORY_DB_PASSWORD=${INVENTORY_DB_PASSWORD}
INVENTORY_DB_URL=postgresql://${INVENTORY_DB_USER}:${INVENTORY_DB_PASSWORD}@${INVENTORY_DB_HOST}:${INVENTORY_DB_PORT}/${INVENTORY_DB_NAME}
EOF

if sudo pm2 describe "$APP_NAME" >/dev/null 2>&1; then
  sudo pm2 delete "$APP_NAME"
fi

sudo pm2 start "$APP_DIR/server.py" \
  --name "$APP_NAME" \
  --cwd "$APP_DIR" \
  --interpreter "$APP_DIR/venv/bin/python"
sudo pm2 save
