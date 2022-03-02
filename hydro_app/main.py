import json
import logging
import sys
import uuid
from threading import Thread
from time import sleep
from typing import Callable, Optional

import pika
import pika.channel
from kivy.app import App
from kivy.config import Config
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from hydro_app.gauge import DialGauge

stderr_handler = logging.StreamHandler(sys.stderr)
logging.getLogger("pika").setLevel(logging.INFO)
logging.getLogger("pika").addHandler(stderr_handler)


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
    spray_interval = ObjectProperty(6)
    spray_duration = ObjectProperty(750)
    min_ph = ObjectProperty(5.8)
    max_ph = ObjectProperty(6.5)
    min_ec = ObjectProperty(1200)
    max_ec = ObjectProperty(1800)
    min_pressure = ObjectProperty(6.0)
    max_pressure = ObjectProperty(8.5)
    picture_interval = ObjectProperty(15)
    paused = ObjectProperty(False)
    pause_button_text = StringProperty("Pause")

    def set_config_values(self, channel, method, props, body):
        self.spray_duration = body["timings"]["spray_box_timings_ms"][0]
        self.spray_interval = body["timings"]["spray_box_interval_ms"] / (60 * 1000)
        self.min_ph = body["levels"]["min_ph"]
        self.max_ph = body["levels"]["max_ph"]
        self.min_ec = body["levels"]["min_ec"]
        self.max_ec = body["levels"]["max_ec"]
        self.min_pressure = body["levels"]["minimum_pressure_bar"]
        self.max_pressure = body["levels"]["maximum_pressure_bar"]

        App.get_running_app().root.ids.sm.get_screen("values").min_ph = self.min_ph
        App.get_running_app().root.ids.sm.get_screen("values").max_ph = self.max_ph
        App.get_running_app().root.ids.sm.get_screen("values").min_ec = self.min_ec
        App.get_running_app().root.ids.sm.get_screen("values").max_ec = self.max_ec
        App.get_running_app().root.ids.sm.get_screen("values").min_pressure = self.min_pressure
        App.get_running_app().root.ids.sm.get_screen("values").max_pressure = self.max_pressure

    def set_system_state(self, body):
        self.paused = body["paused"]
        self.pause_button_text = "Unpause" if self.paused else "Pause"

    def set_paused(self, *args):
        self.paused = True
        self.pause_button_text = "Unpause"

    def set_unpaused(self, *args):
        self.paused = False
        self.pause_button_text = "Pause"

    def pause_button_click(self):
        if self.paused:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "unpause_system", "", lambda c, m, p, b: self.set_unpaused(c, m, p, b)
            )
        else:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "pause_system", "", lambda c, m, p, b: self.set_paused(c, m, p, b)
            )

    def spray_boxes_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("spray_boxes", "")

    def ph_up_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("ph_up", "")

    def ph_down_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("ph_down", "")

    def ec_up_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("ec_up", "")

    def ec_down_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("ec_down", "")

    def empty_tank_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("empty_tank", "")

    def pressure_up_click(self):
        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request("pressure_up", "")

    def update_parameters_click(self):
        if self.spray_interval != self.ids.spray_interval.value or self.spray_duration != self.ids.spray_duration.value:
            self.spray_interval = self.ids.spray_interval.value
            self.spray_duration = self.ids.spray_duration.value

            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_spray_timing", json.dumps({"duration": self.spray_duration, "interval": self.spray_interval})
            )
        if self.min_ph != self.ids.ph_min.value:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_minimum_ph", json.dumps({"ph": self.min_ph})
            )
        if self.max_ph != self.ids.ph_max.value:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_maximum_ph", json.dumps({"ph": self.max_ph})
            )
        if self.min_ec != self.ids.ec_min.value:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_minimum_ec", json.dumps({"ec": self.min_ec})
            )
        if self.max_ec != self.ids.ec_max.value:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_maximum_ec", json.dumps({"ec": self.max_ec})
            )
        if self.min_pressure != self.ids.pressure_min.value:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_minimum_pressure", json.dumps({"pressure": self.min_pressure})
            )
        if self.max_pressure != self.ids.pressure_max.value:
            App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
                "set_maximum_pressure", json.dumps({"pressure": self.max_pressure})
            )

        App.get_running_app().root.ids.sm.get_screen("values").send_rpc_request(
            "set_box_status",
            json.dumps(
                {
                    "box1_status": self.ids.box1_status.active,
                    "box2_status": self.ids.box2_status.active,
                    "box3_status": self.ids.box3_status.active,
                }
            ),
        )


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
    temperature = ObjectProperty(22)
    ph = ObjectProperty(6.34)
    ec = ObjectProperty(1321)
    pressure = ObjectProperty(6.53)

    min_ph = ObjectProperty(4)
    max_ph = ObjectProperty(8)
    min_ec = ObjectProperty(0)
    max_ec = ObjectProperty(2000)
    min_pressure = ObjectProperty(0)
    max_pressure = ObjectProperty(15)

    connection = None
    pending_callbacks = dict()

    def __init__(self, **kw):
        self.start_mq_listener()
        super().__init__(**kw)

    def on_open(self, connection: pika.SelectConnection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        print("Connection opened")
        connection.channel(on_open_callback=self.on_channel_open)
        connection.channel(on_open_callback=self.on_rpc_channel_open)

    def on_channel_open(self, new_channel: pika.channel.Channel):
        """Called when our channel has opened"""
        global channel
        global queue
        print("Channel opened")
        channel = new_channel
        channel.queue_declare(queue="", auto_delete=True, exclusive=True, callback=self.on_queue_declared)

    def on_rpc_channel_open(self, new_channel: pika.channel.Channel):
        global rpc_channel
        print("RPC channel opened")
        rpc_channel = new_channel
        rpc_channel.queue_declare(queue="", auto_delete=True, exclusive=True, callback=self.on_rpc_queue_declared)

    def on_rpc_queue_declared(self, frame):
        print("RPC queue declared")
        global rpc_queue
        rpc_queue = frame.method.queue
        channel.queue_bind(rpc_queue, exchange="rpc_callback")
        rpc_channel.basic_consume(rpc_queue, on_message_callback=self.handle_rpc_callback)

        # get initial readings
        print("Get initial readings")

        def _startup():
            sleep(5)
            self.send_rpc_request(
                "get_system_state",
                "",
                lambda ch, method, properties, body: self.handle_initial_values(ch, method, properties, body),
            )
            sleep(1)
            self.send_rpc_request(
                "get_config", "", App.get_running_app().root.ids.sm.get_screen("control").set_config_values
            )

        Thread(target=_startup).start()

    def send_rpc_request(self, method, body: str, callback: Optional[Callable] = None):
        corr_id = uuid.uuid4().hex
        print(f"Sending rpc request to {method}")
        self.pending_callbacks[corr_id] = callback

        rpc_channel.basic_publish(
            exchange="rpc_data_exchange",
            routing_key=f"rpc.{method}",
            properties=pika.BasicProperties(reply_to=rpc_queue, correlation_id=corr_id),
            body=body,
        )

    def handle_rpc_callback(self, channel, method, props, body):
        print(f"RPC callback gotten: {body}")
        try:
            callback = self.pending_callbacks.get(props.correlation_id)

            if body:
                body = json.loads(body)

            if callback:
                callback(channel, method, props, body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            channel.basic_nack(delivery_tag=method.delivery_tag)
            print(e)
        finally:
            if props.correlation_id in self.pending_callbacks:
                del self.pending_callbacks[props.correlation_id]

    def on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
        print("queue declared")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.temperature")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.ph")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.ec")
        channel.queue_bind(frame.method.queue, exchange="sensor_data_exchange", routing_key="measurement.pressure")

        channel.basic_consume(frame.method.queue, self.handle_sensor_delivery)

    def handle_initial_values(self, channel, method, props, body):
        print("Got initial values")
        self.temperature = round(body.get("last_temperature", 20), 2)
        self.pressure = round(body.get("last_pressure", 6), 2)
        self.ph = round(body.get("last_ph", 6.2), 2)
        self.ec = round(body.get("last_ec", 1300), 0)
        App.get_running_app().root.ids.sm.get_screen("control").set_system_state(body)

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
        Config.set("graphics", "multisamples", "0")
        Config.write()
        return HydroIoT()


def main():
    HydroApp().run()


if __name__ == "__main__":
    main()
