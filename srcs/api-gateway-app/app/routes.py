from flask import Blueprint, request, jsonify
import requests
import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()

api_gateway_bp = Blueprint('api_gateway', __name__)
INVENTORY_URL = os.getenv('INVENTORY_URL')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')


# route inventory service
@api_gateway_bp.route('/api/movies', methods=['GET', 'POST', 'DELETE'])
def movies():
    if request.method == 'GET':
        response = requests.get(f'{INVENTORY_URL}/movies')
        return jsonify(response.json()), response.status_code

    elif request.method == 'POST':
        data = request.get_json()
        response = requests.post(f'{INVENTORY_URL}/movies', json=data)
        # if response.status_code == 201:
            # send_message('movie_added', data)
        return jsonify(response.json()), response.status_code

    elif request.method == 'DELETE':
        data = request.get_json()
        movie_id = data.get('id')
        response = requests.delete(f'{INVENTORY_URL}/movies/{movie_id}')
        # if response.status_code == 200:
        #     send_message('movie_deleted', {'id': movie_id})
        return jsonify(response.json()), response.status_code

@api_gateway_bp.route('/api/movies/<int:movie_id>', methods=['GET', 'PUT', 'DELETE'])
def movie_detail(movie_id):
    if request.method == 'GET':
        response = requests.get(f'{INVENTORY_URL}/movies/{movie_id}')
        return jsonify(response.json()), response.status_code

    elif request.method == 'PUT':
        data = request.get_json()
        response = requests.put(f'{INVENTORY_URL}/movies/{movie_id}', json=data)
        return jsonify(response.json()), response.status_code

    elif request.method == 'DELETE':
        response = requests.delete(f'{INVENTORY_URL}/movies/{movie_id}')
        return jsonify(response.json()), response.status_code
    
# route billing service
@api_gateway_bp.route('/api/billing', methods=['POST'])
def billing():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid input'}), 400
    
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='billing_queue', durable=True)
        channel.basic_publish(exchange='', routing_key='billing_queue', body=json.dumps(data), properties=pika.BasicProperties(delivery_mode=2))
        connection.close()
        return jsonify({'message': 'Billing request sent to RabbitMQ'}), 200
    except Exception as e:
        print(f"Error occurred while publishing message to RabbitMQ: {e}")
        return jsonify({'error': 'Failed to send billing request'}), 500