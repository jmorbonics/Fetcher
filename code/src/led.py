import RPi.GPIO as GPIO
from typing import TypedDict


class PinsConfig(TypedDict):
    pin: int


class Config(TypedDict):
    pins: PinsConfig


class LED:

    pin: int

    def __init__(self, config: Config):
        self.pin = config['pins']['pin']
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
