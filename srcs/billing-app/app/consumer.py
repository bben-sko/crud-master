import pika
import json
import os
import time
from dotenv import load_dotenv
from .models import Session, Order, init_db
load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")


def start_consumer():
    init_db()
    while True:
        try:
            pika_connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = pika_connection.channel()
            channel.queue_declare(queue="billing_queue")
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue="billing_queue", on_message_callback=process_order)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as KeyboardInterrupt:
            break

def process_order(ch, method, properties, body):
    try:
        order_data = json.loads(body)
        session = Session()
        order = Order(
            user_id=order_data["user_id"],
            number_of_items=order_data["number_of_items"],
            total_amount=order_data["total_amount"]
        )
        session.add(order)
        session.commit()
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)