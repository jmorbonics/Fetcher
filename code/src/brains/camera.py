from typing import TypedDict
from picamera2 import Picamera2
import numpy as np


class Config(TypedDict):
    # show_preview=True only works when having a graphical connection to the pi
    show_preview: bool


class Camera:
    cam: Picamera2
    image_array: np.ndarray

    def __init__(self, config: Config):

        self.image_array = np.ndarray(0)

        try:
            self.cam = Picamera2()
            # preview_config = self.cam.create_preview_configuration()
            # preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
            # self.cam.configure(preview_config)
            self.cam.start(show_preview=config['show_preview'])
        
        except:
            self.cam = None

    def capture(self):

        if self.cam != None:
            self.image_array = self.cam.capture_array()
