from typing import TypedDict
from gpiozero import Button


class PinsConfig(TypedDict):
    pin: int


class Config(TypedDict):
    pins: PinsConfig


class Switch(Button):

    """child class of gpiozero.InputDevice, main functionality is instance property 'value'"""

    def __init__(self, config: Config):
        super().__init__(config['pins']['pin'])
        self.state = False
        self.when_released = self.switch_state

    def switch_state(self):
        self.state = not self.state
