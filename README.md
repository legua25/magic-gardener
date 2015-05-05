## THC
# An intelligent automatic sprikler system.

# Requirements

Python 2.7 (see requirements.txt)
Supervisor

Raspberry Pi B+
Arduino Nano
Soil humidity sensor YL-69
Atmospheric pressure sensor BMP180 
Thermometer and ambient humidity sensor DHT11

12v DC power source.
5v 2A USB power source.

# Usage examples
(thc)pi@raspberrypi ~/magic-gardener/tree $ python __init__.py -m 0.7 -t 250 -s /dev/ttyUSB0

# Features

Soil moisture control: 
Using the moisture threshold data and the ambient humidity sensor, by continuously monitoring its state, it will choose an action to keep it under the defined range.
Rain prediction: 
Using onboard sensor information it makes a prediction and chooses an action accordingly.
Water savings: 
Automatic irrigation based on the rain prediction and soil moisture status.

Fully customizable Open Source project, code publicly available at:
https://github.com/legua25/magic-gardener

Sensors:
Atmospheric pressure sensor.
Temperature sensor.
Ambient humidity sensor.
Soil moisture sensor.
