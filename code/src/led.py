from typing import TypedDict
from gpiozero import LED as gpiozero_LED


class PinsConfig(TypedDict):
    pin: int


class Config(TypedDict):
    pins: PinsConfig


class LED(gpiozero_LED):

    """child class of gpiozero.LED, main functionality is self.on(), self.off()"""

    def __init__(self, config: Config):
        super().__init__(config['pins']['pin'])
