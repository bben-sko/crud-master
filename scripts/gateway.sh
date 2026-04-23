#!/usr/bin/env bash
set -e

APP_DIR="${GATEWAY_APP_DIR:-/home/vagrant/api-gateway-app}"
APP_NAME="api-gateway"

cd "$APP_DIR"

python3 -m venv venv
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r requirements.txt

cat > "$APP_DIR/.env" <<EOF
GATEWAY_HOST=${GATEWAY_HOST}
GATEWAY_PORT=${GATEWAY_PORT}
INVENTORY_API_URL=http://${INVENTORY_VM_IP}:${INVENTORY_PORT}
INVENTORY_TIMEOUT=10
RABBITMQ_HOST=${BILLING_VM_IP}
RABBITMQ_PORT=${RABBITMQ_PORT}
RABBITMQ_USER=${RABBITMQ_USER}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
RABBITMQ_QUEUE=${RABBITMQ_QUEUE}
EOF

if sudo pm2 describe "$APP_NAME" >/dev/null 2>&1; then
  sudo pm2 delete "$APP_NAME"
fi

sudo pm2 start "$APP_DIR/server.py" \
  --name "$APP_NAME" \
  --cwd "$APP_DIR" \
  --interpreter "$APP_DIR/venv/bin/python"
sudo pm2 save
