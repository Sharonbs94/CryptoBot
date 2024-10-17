import os
import json
import requests
from config import api_tokens
from kafka import KafkaProducer
from utils.functions import command_url


def fetch_data_from_api_and_send_to_kafka(coin=None, chat_id=None, command=None, currency=None, days=None):
    kafka_broker = os.getenv('KAFKA_BROKERCONNECT', 'kafka:9092')
    kafka_topic = 'user_requests'
    api_data = None 

    url = command_url(command)

    if command == 'cryptocurrency':
        params = {
            'ids': coin,
            'vs_currencies': currency
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if coin in data and currency in data[coin]:
                price = data[coin][currency]

                api_data = {
                    'coin': coin,
                    'currency': currency,
                    'chat_id': chat_id,
                    'price': price,
                    'command': command
                }
            else:
                print("Coin or currency not found in the API response.")
        else:
            print(f"API request failed with status code {response.status_code}.")

    elif command == 'graph':
        params = {
            'ids': coin,
            'vs_currencies': currency,
            'days': days
        }

        formatted_url = url.format(id=params['ids'], currency=params['vs_currencies'], days=params['days'])

        response = requests.get(formatted_url)

        if response.status_code == 200:
            data = response.json()

            api_data = {
                'coin': coin,
                'currency': currency,
                'days': days,
                'chat_id': chat_id,
                'data': data,
                'command': command
            }
        else:
            print(f"API request failed with status code {response.status_code}.")

    elif command == 'news':
        params = {
            'auth_token': api_tokens.CRYPTOPANIC_TOKEN,
            'currencies': coin,
            'kind': 'news'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            api_data = {
                'coin': coin,
                'chat_id': chat_id,
                'data': data,
                'command': command
            }
        else:
            print(f"API request failed with status code {response.status_code}.")
    else:
        print(f"Invalid command: {command}")

    if api_data:
        producer = KafkaProducer(
            bootstrap_servers=kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        try:
            producer.send(kafka_topic, value=api_data)
            producer.flush()
            producer.close()
            print(f"Data sent to Kafka topic '{kafka_topic}': {api_data}")
        except Exception as e:
            print(f"Error sending data to Kafka: {e}")
    else:
        print("No data to send to Kafka.")