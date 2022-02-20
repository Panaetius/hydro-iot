import json
import os
from threading import Thread

import pika
import pika.channel
from kivy.app import App
from kivy.config import Config
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager


class HydroIoT(BoxLayout):
    pass


class HydroScreenManager(ScreenManager):
    def switch_screen(self, screen):
        direction = "right"

        if screen == "settings" or screen == "control" and self.current == "values":
            direction = "left"

        self.transition.direction = direction
        self.current = screen


class ControlScreen(Screen):
    pass


class SettingsScreen(Screen):
    host = StringProperty()
    user = StringProperty()
    password = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.host = Config.getdefault("hydroiot", "host", "")
        self.user = Config.getdefault("hydroiot", "user", "")
        self.password = Config.getdefault("hydroiot", "password", "")

    def save_settings(self, *args):
        Config.set("hydroiot", "host", self.host)
        Config.set("hydroiot", "user", self.user)
        Config.set("hydroiot", "password", self.password)
        Config.write()
        App.get_running_app().root.ids.sm.get_screen("values").stop_mq_listener()
        App.get_running_app().root.ids.sm.get_screen("values").start_mq_listener()


class MainScreen(Screen):
    temperature = ObjectProperty(None)
    ph = ObjectProperty(None)
    ec = ObjectProperty(None)
    pressure = ObjectProperty(None)

    connection = None

    def __init__(self, **kw):
        self.start_mq_listener()
        super().__init__(**kw)

    def on_open(self, connection: pika.SelectConnection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        print("Connection opened")
        connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, new_channel: pika.channel.Channel):
        """Called when our channel has opened"""
        global channel
        global queue
        print("Channel opened")
        channel = new_channel
        channel.queue_declare(queue="", exclusive=True, callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
        print("queue declared")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.temperature")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.ph")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.ec")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.pressure")

        channel.basic_consume(frame.method.queue, self.handle_sensor_delivery)

    def handle_sensor_delivery(self, channel: pika.channel.Channel, method, header, body):
        """Called when we receive a message from RabbitMQ"""
        body = json.loads(body.decode())
        routing_key = method.routing_key
        print(f"Received msg: {body}")

        if routing_key == "measurement.temperature":
            self.temperature = round(float(body["temperature"]), 2)
        elif routing_key == "measurement.ph":
            self.ph = round(float(body["ph"]), 2)
        elif routing_key == "measurement.ec":
            self.ec = round(float(body["ec"]), 0)
        elif routing_key == "measurement.pressure":
            self.pressure = round(float(body["pressure"]), 2)
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def on_error(self, *args):
        print(f"Error: {args}")

    def start_mq_listener(self):
        host = Config.getdefault("hydroiot", "host", None)
        user = Config.getdefault("hydroiot", "user", None)
        password = Config.getdefault("hydroiot", "password", None)
        print(user)
        print(password)

        if not host or not user or not password:
            return

        parameters = pika.ConnectionParameters(
            host=host,
            credentials=pika.PlainCredentials(username=user, password=password),
        )
        self.connection = pika.SelectConnection(
            parameters, on_open_callback=self.on_open, on_open_error_callback=self.on_error
        )
        print("setting up connection")

        def _start_connection(connection):
            try:
                print("starting connection")
                # Loop so we can communicate with RabbitMQ
                self.connection.ioloop.start()
            except KeyboardInterrupt:
                # Gracefully close the connection
                self.connection.close()

        Thread(target=_start_connection, args=(self.connection,)).start()

    def stop_mq_listener(self):
        if self.connection:
            try:
                self.connection.close()
            except:
                pass


class HydroApp(App):
    def build(self):
        Config.adddefaultsection("hydroiot")
        return HydroIoT()


def main():
    HydroApp().run()


if __name__ == "__main__":
    main()
