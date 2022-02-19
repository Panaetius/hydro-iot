import json
import logging
import os

import cysystemd.daemon as daemon
import pika
import pika.channel
import psycopg2
from dotenv import load_dotenv

logging.info("Starting up.")

# Create a global channel variable to hold our channel object in
channel: pika.channel.Channel = None


def on_open(connection: pika.SelectConnection):
    """Called when we are fully connected to RabbitMQ"""
    # Open a channel
    connection.channel(on_open_callback=on_channel_open)


def on_channel_open(new_channel: pika.channel.Channel):
    """Called when our channel has opened"""
    global channel
    channel = new_channel
    channel.queue_declare(
        queue="sensor_data", durable=True, exclusive=False, auto_delete=False, callback=on_queue_declared
    )


def on_queue_declared(frame):
    """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
    channel.basic_consume("sensor_data", handle_sensor_delivery)


def handle_sensor_delivery(channel, method, header, body):
    """Called when we receive a message from RabbitMQ"""
    body = json.loads(body.decode())
    routing_key = method.routing_key

    if routing_key == "measurement.temperature":
        handle_temperature(body, header.timestamp)
    elif routing_key == "measurement.ph":
        handle_ph(body, header.timestamp)
    elif routing_key == "measurement.ec":
        handle_ec(body, header.timestamp)
    elif routing_key == "measurement.pressure":
        handle_pressure(body, header.timestamp)
    else:
        return

    channel.basic_ack(delivery_tag=method.delivery_tag)


def handle_temperature(body, timestamp):
    insert_data(
        "INSERT INTO hydroponics.temperature_data (water_temp, timestamp) VALUES (%s, %s);",
        (body["temperature"], timestamp),
    )


def handle_ph(body, timestamp):
    insert_data("INSERT INTO hydroponics.ph_data (ph, timestamp) VALUES (%s, %s);", (body["ph"], timestamp))


def handle_ec(body, timestamp):
    insert_data("INSERT INTO hydroponics.ec_data (ec, timestamp) VALUES (%s, %s);", (body["ec"], timestamp))


def handle_pressure(body, timestamp):
    insert_data(
        "INSERT INTO hydroponics.pressure_data (pressure, timestamp) VALUES (%s, %s);", (body["pressure"], timestamp)
    )


def insert_data(sql_statement, values):
    connection = None
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="hydroponics",
            user="zenon",
            password=None,
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                sql_statement,
                values,
            )
    finally:
        if connection:
            connection.close()


load_dotenv()


parameters = pika.ConnectionParameters(
    host=os.environ.get("RABBITMQ_HOST"),
    credentials=pika.PlainCredentials(
        username=os.environ.get("RABBITMQ_USERNAME"), password=os.environ.get("RABBITMQ_PASSWORD")
    ),
)
connection = pika.SelectConnection(parameters, on_open_callback=on_open)

try:
    logging.info("Startup complete")
    # Tell systemd that our service is ready
    daemon.notify(daemon.Notification.READY)

    # Loop so we can communicate with RabbitMQ
    connection.ioloop.start()
except KeyboardInterrupt:
    # Gracefully close the connection
    connection.close()
    # Loop until we're fully closed, will stop on its own
    connection.ioloop.start()
