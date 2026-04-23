# Movie Streaming Platform

This repository contains a small microservices platform composed of three Python services:

- `inventory-api`: a Flask CRUD API backed by PostgreSQL.
- `billing-consumer`: a RabbitMQ consumer that stores orders in PostgreSQL.
- `api-gateway`: a Flask gateway that proxies movie requests over HTTP and publishes billing requests to RabbitMQ.

The stack is designed to run either manually from each service directory or through three dedicated Vagrant virtual machines managed with PM2.

## Architecture

- `gateway-vm`
  - Runs `api-gateway`
  - Exposes `http://localhost:3000`
- `inventory-vm`
  - Runs `inventory-api`
  - Hosts PostgreSQL database `movies_db`
  - Exposes `http://localhost:8080`
- `billing-vm`
  - Runs `billing-consumer`
  - Hosts RabbitMQ and PostgreSQL database `billing_db`
  - Exposes RabbitMQ management UI at `http://localhost:15672`

Communication flow:

- Client -> API Gateway -> Inventory API via HTTP
- Client -> API Gateway -> RabbitMQ -> Billing consumer

## Repository Layout

```text
.
├── .env
├── README.md
├── Vagrantfile
├── config.yaml
├── docs
│   └── openapi.yaml
├── postman
│   ├── movie-streaming-platform.postman_collection.json
│   └── movie-streaming-platform.postman_environment.json
├── scripts
│   ├── billing.sh
│   ├── gateway.sh
│   ├── global.sh
│   └── inventory.sh
└── srcs
    ├── api-gateway-app
    ├── billing-app
    └── inventory-app
```

## Prerequisites

Install these tools on the host machine:

- Python 3
- PostgreSQL
- RabbitMQ
- Vagrant
- VirtualBox
- Postman or an equivalent API client

The Vagrant workflow installs Python dependencies, PostgreSQL, RabbitMQ, Node.js, and PM2 inside the guest machines.

## Environment Variables

The project is fully configured from the committed root `.env` file. No service has credentials hard-coded in source files.

Defined variables:

- `GATEWAY_VM_IP`
- `GATEWAY_HOST`
- `GATEWAY_PORT`
- `INVENTORY_API_URL`
- `INVENTORY_VM_IP`
- `INVENTORY_HOST`
- `INVENTORY_PORT`
- `INVENTORY_DB_HOST`
- `INVENTORY_DB_PORT`
- `INVENTORY_DB_NAME`
- `INVENTORY_DB_USER`
- `INVENTORY_DB_PASSWORD`
- `BILLING_VM_IP`
- `BILLING_DB_HOST`
- `BILLING_DB_PORT`
- `BILLING_DB_NAME`
- `BILLING_DB_USER`
- `BILLING_DB_PASSWORD`
- `BILLING_RETRY_DELAY`
- `RABBITMQ_PORT`
- `RABBITMQ_MANAGEMENT_PORT`
- `RABBITMQ_HOST`
- `RABBITMQ_USER`
- `RABBITMQ_PASSWORD`
- `RABBITMQ_QUEUE`

During provisioning, the Vagrant shell scripts transform these values into service-specific `.env` files inside each application directory.

## Running the Services Manually

You can run every service without Vagrant. Create a dedicated virtual environment for each service first.

### 1. Inventory API

```bash
cd srcs/inventory-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Expected endpoint:

- `http://localhost:8080/api/movies`

Required PostgreSQL database:

- Database: `movies_db`
- Table: `movies`
- Credentials: match the values in the root `.env`

### 2. Billing Consumer

```bash
cd srcs/billing-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

This service does not expose HTTP endpoints. It consumes persistent messages from `billing_queue`.

Required infrastructure:

- PostgreSQL database: `billing_db`
- Table: `orders`
- RabbitMQ queue: `billing_queue`
- RabbitMQ credentials: match the values in the root `.env`

### 3. API Gateway

```bash
cd srcs/api-gateway-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Expected endpoint:

- `http://localhost:3000`
- The gateway expects the inventory and RabbitMQ values from the root `.env`

## Running the Full Platform with Vagrant

From the repository root:

```bash
vagrant up
vagrant status
```

Useful VM commands:

```bash
vagrant ssh gateway-vm
vagrant ssh inventory-vm
vagrant ssh billing-vm
```

Provisioning summary:

- `scripts/global.sh`
  - Installs Python, Node.js, and PM2
- `scripts/inventory.sh`
  - Installs PostgreSQL
  - Creates `movies_db`
  - Starts `inventory-api` with PM2
- `scripts/billing.sh`
  - Installs PostgreSQL and RabbitMQ
  - Creates `billing_db`
  - Creates the RabbitMQ user and permissions
  - Starts `billing-consumer` with PM2
- `scripts/gateway.sh`
  - Writes gateway configuration
  - Starts `api-gateway` with PM2

## PM2 Commands

Inside the corresponding VM:

```bash
sudo pm2 list
sudo pm2 stop api-gateway
sudo pm2 start api-gateway
sudo pm2 stop inventory-api
sudo pm2 start inventory-api
sudo pm2 stop billing-consumer
sudo pm2 start billing-consumer
```

PM2 is used so the audit can stop and restart services easily while leaving RabbitMQ alive.

## API Summary

### Inventory API

- `GET /api/movies`
- `GET /api/movies?title=<name>`
- `POST /api/movies`
- `DELETE /api/movies`
- `GET /api/movies/<id>`
- `PUT /api/movies/<id>`
- `DELETE /api/movies/<id>`

Example create request:

```json
{
  "title": "The Matrix",
  "description": "A hacker discovers the nature of his reality."
}
```

### Billing Through the Gateway

- `POST /api/billing`

Example request:

```json
{
  "user_id": "3",
  "number_of_items": "5",
  "total_amount": "180"
}
```

The gateway only publishes the request body to RabbitMQ. The billing consumer processes queued messages independently and stores them in `billing_db.orders`.

## RabbitMQ Test Flow

1. Start the platform with `vagrant up`.
2. Open `http://localhost:15672`.
3. Log in with the RabbitMQ credentials defined in `.env`.
4. Publish a JSON message to `billing_queue`, or send `POST /api/billing` to the gateway.
5. Confirm rows appear in `billing_db.orders`.
6. Stop the consumer with `sudo pm2 stop billing-consumer`.
7. Send another `POST /api/billing` request. The gateway should still return success.
8. Restart the consumer with `sudo pm2 start billing-consumer`.
9. Confirm pending messages are processed from the queue.

## Postman Assets

Reusable Postman files are provided in `postman/`:

- `postman/movie-streaming-platform.postman_collection.json`
- `postman/movie-streaming-platform.postman_environment.json`

The collection covers:

- every inventory endpoint
- a billing message publish through the gateway

Import both files into Postman, select the environment, then run the requests in order.

## OpenAPI Documentation

The API Gateway OpenAPI specification is available at:

- `docs/openapi.yaml`

It documents:

- movie proxy endpoints
- the billing publish endpoint
- request and response schemas

## Design Choices

- Flask was used for both HTTP services because the subject explicitly targets a lightweight Python REST setup.
- SQLAlchemy is used for relational persistence in both data-owning services.
- RabbitMQ is isolated on `billing-vm` so billing requests remain accepted even while the billing consumer process is stopped.
- The gateway forwards inventory responses without re-shaping them, which keeps the gateway thin and predictable.
- Service configuration is centralized in the committed root `.env` file, then distributed per VM during provisioning.
