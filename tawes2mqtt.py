import json
import logging
import time

import requests
import csv
import paho.mqtt.client as mqtt

logger = logging.getLogger()

# Weather data and station
TAWES_URL = "https://www.zamg.ac.at/ogd/"
DESIRED_STATION = "11331"  # Klagenfurt/Flughafen

# MQTT configuration
MQTT_BROKER_IP = "10.0.0.30"
BASE_TOPIC = "homeassistant/sensor/tawes/"
BASE_ID = "tawes_weather_"
mqtt.Client.connected_flag = False

IGNORE_KEYS = ['station', 'name', 'sea_level', 'date', 'time', 'peak_wind_direction', 'peak_wind_speed']

STATION_PARAMS = {
    "station": {"key": "Station", "name": "Station", "device_class": "", "unit": ""},
    "name": {"key": "Name", "name": "Name", "device_class": "", "unit": ""},
    "sea_level": {"key": "Höhe m", "name": "Seehöhe", "device_class": "", "unit": "m"},
    "date": {"key": "Datum", "name": "Datum", "device_class": "date", "unit": ""},
    "time": {"key": "Zeit", "name": "Zeit", "device_class": "timestamp", "unit": ""},
    "temperature": {"key": "T °C", "name": "Temperature", "device_class": "temperature", "unit": "°C"},
    "dewpoint": {"key": "TP °C", "name": "Dewpoint", "device_class": "temperature", "unit": "°C"},
    "humidity": {"key": "RF %", "name": "Relative Humidity", "device_class": "humidity", "unit": "%"},
    "wind_direction": {"key": "WR °", "name": "Avg. Wind Direction", "device_class": "signal_strength", "unit": "°"},
    "wind_speed": {"key": "WG km/h", "name": "Avg. Wind Speed", "device_class": "signal_strength", "unit": "km/h"},
    "peak_wind_direction": {"key": "WSR °", "name": "Peak Wind Direction", "device_class": "", "unit": "°"},
    "peak_wind_speed": {"key": "WSG km/h", "name": "Peak Wind Speed", "device_class": "", "unit": "km/h"},
    "percipitation": {"key": "N l/m²", "name": "Percipitation", "device_class": "humidity", "unit": "l/m²"},
    "relative_pressure": {"key": "LDred hP", "name": "Relative Pressure", "device_class": "pressure", "unit": "hPa"},
    "absolute_pressure": {"key": "LDstat hPa", "name": "Absolute Pressure", "device_class": "pressure", "unit": "hPa"},
    "sunshine": {"key": "SO %", "name": "Sunshine per hour", "device_class": "illuminance", "unit": "%"}
}


def read_tawes():
    r = requests.get(TAWES_URL)
    return (line.decode("utf-8") for line in r.iter_lines())


def get_station_weather(station_weather_datasets, station_id):
    station_weather = dict()
    station_dataset = dict()

    # create dict from TAWES-csv
    for row in csv.DictReader(station_weather_datasets, delimiter=";"):

        # only get weather data for the given station_id
        if row[STATION_PARAMS["station"]["name"]] == station_id:
            station_dataset = row

    # create a dictionary using keys from STATION_PARAMS and values from station weather data
    for param_key, param_value in STATION_PARAMS.items():
        for station_key, station_value in station_dataset.items():
            if param_value['key'] == station_key and param_key not in IGNORE_KEYS:
                station_weather[param_key] = station_value

    return station_weather


def mqtt_publish_config(mqtt_client):
    for param in STATION_PARAMS.keys():
        if param in IGNORE_KEYS:
            return

        name = STATION_PARAMS[param]["name"]  # Entity name listed in HASS (Home Assistant) (e.g. "Temperature")
        device_class = STATION_PARAMS[param]["device_class"]  # defines the icon used in HASS (e.g. "temperature")
        unit = STATION_PARAMS[param]["unit"]  # defines the unit used in HASS (e.g. "°C")
        unique_id = f"{BASE_ID}{param}"  # unique identifier used in HASS (e.g. "tawes_temperature")
        value_template = f"{{{{ value_json.{unique_id}}}}}"  # defines how HASS extracts the value of this entity
        topic = f"{BASE_TOPIC}{unique_id}/config"

        payload = {
            "device_class": device_class,
            "name": f"{name} Fernwärme",
            "state_topic": f"{BASE_TOPIC}state",
            "unit_of_measurement": unit,
            "value_template": value_template,
            "unique_id": unique_id
        }

        mqtt_client.publish(topic, payload=json.dumps(payload), qos=2)


def mqtt_publish_state(mqtt_client, weather_data):
    topic = f"{BASE_TOPIC}state"
    payload = dict()
    for key, value in weather_data.items():
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                continue

        payload[f"{BASE_ID}{key}"] = value

    mqtt_client.publish(topic, payload=json.dumps(payload), qos=2)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        logger.debug("connected OK")
    else:
        logger.debug("Bad connection Returned code=", rc)


def mqtt_run(station_weather):
    mqtt_client = mqtt.Client("tawes")
    logger.debug(f"Connecting to mqtt_broker_ip {MQTT_BROKER_IP}")

    mqtt_client.connect(MQTT_BROKER_IP)
    mqtt_client.on_connect = on_connect

    mqtt_client.loop_start()

    while not mqtt_client.connected_flag:
        logger.debug("In mqtt connect wait loop")
        time.sleep(1)
    logger.debug("Connected to mqtt broker")

    mqtt_publish_config(mqtt_client)
    mqtt_publish_state(mqtt_client, station_weather)

    mqtt_client.loop_stop()
    mqtt_client.disconnect()


if __name__ == "__main__":
    station_weather_datasets = read_tawes()
    station_weather = get_station_weather(station_weather_datasets, DESIRED_STATION)
    mqtt_run(station_weather)
