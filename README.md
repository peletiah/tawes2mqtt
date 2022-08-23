# TAWES to MQTT

## About
This script fetches weather data from [TAWES](https://www.zamg.ac.at/cms/de/images/klima/bild_messnetze/tawes-messinstrumente) (**T**eil **A**utomatisches **W**etter **E**rfassungs **S**ystem) of [ZAMG](https://www.zamg.ac.at), extracts data for a defined station and publishes it via MQTT (Formatted for [automatic discovery](https://www.home-assistant.io/docs/mqtt/discovery/) in [Home Assistant](https://www.home-assistant.io/))

## Installation
Fetch source via git:
      
    git clone https://github.com/peletiah/tawes2mqtt.git
    cd tawes2mqtt/

Prepare the virtualenv and activate environment:

    virtualenv -p python3 . 
    source bin/activate

Install requirements with pip:

    pip install -r requirements.txt

## Configuration
In `tawes2mqtt.py` edit the settings according to your requirements:


##### Weather station and weather data 
This script only publishes weather data from a single station. The setting `DESIRED_STATION` defines which station is selected (Default: `11331`, which is the weatherstation at Klagenfurt/Flughafen). The station-ID can be found in the first column of the TAWES [csv-file](https://www.zamg.ac.at/ogd/) from ZAMG's website.

- `DESIRED_STATION` defines the ID of the station of which weather data should be published
- `IGNORE KEYS` defines weather parameters that should not be published via MQTT(e.g. the station's ID and name, height above sea level, peak wind speed, ...)

##### MQTT configuration
- `MQTT_BROKER_IP` defines the IP-address of the MQTT-Broker we publish to
- `BASE_TOPIC` defines a string that is prepended to the MQTT-topic
- `BASE_ID` defines a string that is prepended to the weather-parameter-keys (e.g. `humidity` becomes `my_base_id_humidity`)
- `NAME_SUFFIX` defines a string that is affixed to parameter name (e.g. `Relative Humidity` becomes `Relative Humidity my name suffix`)
- `MQTT_QOS` define the MQTT QOS level - default is 2, which guarantees the delivery of the message (see [Understanding MQTT QOS Levels](http://www.steves-internet-guide.com/understanding-mqtt-qos-levels-part-1/)
- `MQTT_RETAIN` if `True`, tells the broker to keep the last message until overwritten (see [MQTT Retain Explanation](http://www.steves-internet-guide.com/mqtt-retained-messages-example/))

#### STATION_PARAMS

The `STATION_PARAMS`-dictionary provides mapping of data-format from the keys in the TAWES csv-file to a more programmer-friendly format (e.g. `LDstat hPa` is mapped to `relative_pressure`). Additional key-value-pairs for each parameter are added for convenience. Most of these additional values are specifically for the [Home Assistant MQTT discovery](https://www.home-assistant.io/docs/mqtt/discovery/)

`STATION_PARAMS`

`param_name` - distinguishable and human-readable name of the parameter (e.g. `relative_pressure`)

&emsp;`key` - ZAMG TAWES column name (e.g. `LDstat hPa`)

&emsp;`name` - Name of the parameter, used for "entity name" in Home Assistant

&emsp;`device_class` - Defines the entity icon that is used in Home Assistant (see [Device Class](https://www.home-assistant.io/integrations/sensor/))

&emsp;`unit` - Defines the unit of the parameter, used as the unit-option in Home Assistant

## Execution

The script can be executed manually like this:

    /my/virtualenv/bin/python /my/virtualenv/tawes2mqtt.py

Or through a cronjob (Notice: ZAMG publishes new data ~20 minutes past the full hour, to have some leeway the script is executed every 30 minutes past the full hour):

    30 * * * * myuser /my/virtualenv/tawes2mqtt/bin/python /my/virtualenv/tawes2mqtt/tawes2mqtt.py
