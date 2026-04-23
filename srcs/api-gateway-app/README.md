# API Gateway — crud-master

## Overview

The API Gateway is a Python Flask application that acts as the **single entry point**
for all client requests. It routes traffic to the appropriate microservice:

- **Inventory API** → via HTTP (REST)
- **Billing API** → via RabbitMQ (async message queue)

---

## Concepts

### What is an API Gateway?
An API Gateway is a server that acts as a reverse proxy — it receives all incoming
requests from clients and forwards them to the correct backend service.
The client never communicates directly with the services.

### What is RabbitMQ?
RabbitMQ is a message broker. Instead of calling the Billing API directly via HTTP,
the gateway publishes a JSON message to a queue (`billing_queue`).
The Billing API consumes messages from that queue asynchronously.

This means:
- If the Billing API is **stopped**, messages stay in the queue safely.
- When it **restarts**, it processes all pending messages automatically.

### What is pika?
`pika` is the official Python library to interface with RabbitMQ using the AMQP protocol.

### What is durable queue?
A durable queue survives RabbitMQ restarts. Combined with `delivery_mode=2`
(persistent messages), no data is lost even if the server crashes.

---

## Project Structure
`api-gateway-app/
├── server.py # Entry point — starts Flask on port 3000
├── requirements.txt # Python dependencies
└── app/
├── _init_.py # Flask app factory
└── routes.py # All gateway routes

`

---

## Requirements

```txt
flask
requests
pika
python-dotenv
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file at the root of the project:

```env
INVENTORY_URL=http://192.168.56.11:8080
RABBITMQ_HOST=192.168.56.12
GATEWAY_PORT=3000
```

---

## Endpoints

| Method | Endpoint | Description | Protocol |
|--------|----------|-------------|----------|
| GET | `/api/movies` | Get all movies | HTTP → Inventory |
| GET | `/api/movies?title=[name]` | Search movies by title | HTTP → Inventory |
| POST | `/api/movies` | Create a new movie | HTTP → Inventory |
| DELETE | `/api/movies` | Delete all movies | HTTP → Inventory |
| GET | `/api/movies/<id>` | Get movie by ID | HTTP → Inventory |
| PUT | `/api/movies/<id>` | Update movie by ID | HTTP → Inventory |
| DELETE | `/api/movies/<id>` | Delete movie by ID | HTTP → Inventory |
| POST | `/api/billing` | Send billing order | RabbitMQ → Billing |

---

## How to Run

### Locally (development)
```bash
cd srcs/api-gateway-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

### With PM2 (inside gateway-vm)
```bash
pm2 start server.py --interpreter venv/bin/python3 --name api-gateway
pm2 save
```

---

## How to Test

### Test Inventory routing
```bash
curl http://localhost:3000/api/movies
curl -X POST http://localhost:3000/api/movies \
  -H "Content-Type: application/json" \
  -d '{"title": "Inception", "description": "A mind-bending thriller"}'
```

### Test Billing routing
```bash
curl -X POST http://localhost:3000/api/billing \
  -H "Content-Type: application/json" \
  -d '{"user_id": "3", "number_of_items": "5", "total_amount": "180"}'
```

Expected response:
```json
{ "message": "Message posted" }
```

---

## Design Choices

- **Flask** was chosen for its simplicity and lightweight nature — the gateway
  does not need a heavy framework since it only proxies requests.
- **pika** is used for RabbitMQ communication — it is the official Python AMQP client.
- **durable=True + delivery_mode=2** ensures no messages are lost if the Billing
  service is temporarily down.
- **Environment variables** via `.env` keep all credentials and URLs configurable
  without hardcoding anything in the source code.