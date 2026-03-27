#!/usr/bin/python3
"""\
This script controls the power led.
"""

__author__ = "Olaf Splitt"
__license__ = "GPLv3"
__version__ = "1.0.1"
__email__ = "splitti@mupibox.de"
__status__ = "dev"


import os
import signal
import sys
import json
from time import sleep
#import RPi.GPIO as GPIO
import gpiozero

DEFAULT_PWM_FREQUENCY = 3000


import os
import signal
import sys
import json
from time import sleep
from gpiozero import PWMLED

DEFAULT_PWM_FREQUENCY = 3000  # wird von gpiozero ignoriert (nicht nötig)


def read_json():
    try:
        with open(JSON_DATA_FILE) as file:
            rc = json.loads(file.read())
    except:
        rc = "skip"
    return rc


def led_control(start, end, sleep_time):
    step = 1 if start < end else -1

    for x in range(start, end, step):
        try:
            POWER_LED.value = x / 100.0
        except:
            pass
        sleep(sleep_time)

    try:
        POWER_LED.value = end / 100.0
    except:
        pass

    print("LED Brightness = " + str(end) + "%")


def sigterm_handler(*_):
    led_control(JSON_DATA["led_max_brightness"], 0, 0.003)

    for _ in range(3):
        led_control(0, JSON_DATA["led_max_brightness"], 0.003)
        led_control(JSON_DATA["led_max_brightness"], 0, 0.003)

    sys.exit(0)


def init():
    tmp = os.popen(
        "ps -ef | grep chromium-browser | grep http | grep -v grep"
    ).read()

    while tmp == "":
        for _ in range(10):
            led_control(0, JSON_DATA["led_max_brightness"], 0.003)
            led_control(JSON_DATA["led_max_brightness"], 0, 0.003)
        tmp = os.popen(
            "ps -ef | grep chromium-browser | grep http | grep -v grep"
        ).read()

    led_control(0, JSON_DATA["led_max_brightness"], 0.01)


def main():
    global JSON_DATA

    LED_DIM_MODE_LAST = JSON_DATA["led_dim_mode"]

    while True:
        JSON_DATA = read_json()

        if JSON_DATA != "skip":

            if JSON_DATA["led_dim_mode"] == "0" and JSON_DATA["led_dim_mode"] != LED_DIM_MODE_LAST:
                led_control(JSON_DATA["led_min_brightness"],
                            JSON_DATA["led_max_brightness"], 0.02)

            if JSON_DATA["led_dim_mode"] == "1" and JSON_DATA["led_dim_mode"] != LED_DIM_MODE_LAST:
                led_control(JSON_DATA["led_max_brightness"],
                            JSON_DATA["led_min_brightness"], 0.02)

            LED_DIM_MODE_LAST = JSON_DATA["led_dim_mode"]

        sleep(1)


if __name__ == "__main__":
    JSON_DATA_FILE = "/tmp/.power_led"

    JSON_DATA = "skip"
    while JSON_DATA == "skip":
        JSON_DATA = read_json()

    # gpiozero PWM LED
    POWER_LED = PWMLED(JSON_DATA["led_gpio"])

    init()

    signal.signal(signal.SIGTERM, sigterm_handler)

    main()
