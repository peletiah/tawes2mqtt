# TAWES to MQTT

## About
This script fetches weather data from [TAWES](https://www.zamg.ac.at/cms/de/images/klima/bild_messnetze/tawes-messinstrumente) (**T**eil **A**utomatisches **W**etter **E**rfassungs **S**ystem) of [ZAMG](https://www.zamg.ac.at), extracts data for a defined station and publishes it via MQTT (Formatted for import in [Home Assistant](https://www.home-assistant.io/))

## Installation
Prepare a virtualenv and activate environment:

    $ virtualenv -p python3 tawes2mqtt
    $ cd tawes2mqtt/
    $ source bin/activate


Fetch source via git:
      
    $ git clone https://github.com/peletiah/tawes2mqtt.git

Install requirements with pip:

    $ pip install -r requirements.txt

## Configuration
In 





