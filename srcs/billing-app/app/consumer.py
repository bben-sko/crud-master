import json
import os
import time
from decimal import Decimal, InvalidOperation

import pika
from dotenv import load_dotenv

from .models import Order, SessionLocal, init_db


load_dotenv()


def rabbitmq_queue():
    return os.getenv("RABBITMQ_QUEUE", "billing_queue")


def retry_delay():
    return int(os.getenv("BILLING_RETRY_DELAY", "5"))


def build_rabbitmq_parameters():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "guest"),
        os.getenv("RABBITMQ_PASSWORD", "guest"),
    )
    return pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=credentials,
    )


def process_order(ch, method, _properties, body):
    session = SessionLocal()

    try:
        payload = json.loads(body.decode("utf-8"))
        order = Order(
            user_id=str(payload["user_id"]),
            number_of_items=int(payload["number_of_items"]),
            total_amount=Decimal(str(payload["total_amount"])),
        )
        session.add(order)
        session.commit()
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, InvalidOperation) as exc:
        session.rollback()
        print(f"Discarding invalid billing message: {exc}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as exc:
        session.rollback()
        print(f"Billing message processing failed, requeueing: {exc}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    finally:
        session.close()


def run_consumer():
    init_db()

    while True:
        connection = None
        try:
            connection = pika.BlockingConnection(build_rabbitmq_parameters())
            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_queue(), durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=rabbitmq_queue(),
                on_message_callback=process_order,
            )
            print("Billing consumer is waiting for messages")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as exc:
            print(f"RabbitMQ unavailable, retrying in {retry_delay()} seconds: {exc}")
            time.sleep(retry_delay())
        except KeyboardInterrupt:
            if connection and connection.is_open:
                connection.close()
            break
        except Exception as exc:
            print(f"Billing consumer crashed, retrying in {retry_delay()} seconds: {exc}")
            if connection and connection.is_open:
                connection.close()
            time.sleep(retry_delay())
