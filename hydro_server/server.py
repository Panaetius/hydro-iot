import datetime
import sys

import psycopg2
import requests

ip = "192.168.1.138"

session = requests.Session()
response = session.get(f"http://{ip}/", timeout=5)
data = response.json()

ec = data["ec"]
pH = data["ph"]
waterTemp = data["waterTemp"]
boxTemp = data["boxTemp"] if "boxTemp" in data and float(data["boxTemp"]) > 0 else None
boxHumidity = data["boxHumidity"] if "boxHumidity" in data and float(data["boxHumidity"]) > 0 else None
fogState = "foggerState" in data and data["foggerState"] == 1
hpaPressure = data["hpaPressure"] if "hpaPressure" in data else 0
fanRpm = data["rpm"] if "rpm" in data else 0

connection = psycopg2.connect(
    host="localhost",
    database="hydroponics",
    user="zenon",
    password=None,
)
connection.autocommit = True
if float(ec) < 300 or float(ec) > 3000:
    # correct when fogger on
    ec = None
if float(waterTemp) < 10 or float(waterTemp) > 40:
    waterTemp = None

if float(pH) < 4 or float(pH) > 7.5:
    pH = None

with connection.cursor() as cursor:
    cursor.execute(
        f"INSERT INTO hydroponics.sensor_data (water_temp, ec, ph, box_temp, box_humidity, rpm, fog_state, hpa_pressure, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
        (waterTemp, ec, pH, boxTemp, boxHumidity, fanRpm, fogState, hpaPressure, datetime.datetime.now()),
    )
