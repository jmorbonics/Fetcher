from typing import TypedDict
from voice_control import run_mic, language2UTF8, gpt_query
from yolo_opencv_fetcher import detect, get_output_layers, draw_prediction
from .. import vehicle as vehicle_module, camera as camera_module, distance_sensor as distance_sensor_module, led as led_module, switch as switch_module
import time
import pyaudio
import numpy as np
import os
import pvporcupine
from pvrecorder import PvRecorder
import wave
import struct
from google.cloud import speech_v1p1beta1 as speech
import openai
from openai import OpenAI
from dotenv import load_dotenv

CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../fetcher-415315-deae76a1ddb7.json"
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PICOVOICE_KEY = os.getenv("PICOVOICE_API_KEY")


class Config(TypedDict):
    sample_hz: int


class Brain:

    """The base Brain object, which all other Brains should inherit"""

    camera: camera_module.Camera
    vehicle: vehicle_module.Vehicle
    distance_sensors: list[distance_sensor_module.DistanceSensor]
    running: bool
    switches: list[switch_module.Switch]
    leds: list[led_module.LED]
    sample_hz: int
    loop_counter: int

    def __init__(self, config: Config,
                 camera: camera_module.Camera,
                 distance_sensors: list[distance_sensor_module.DistanceSensor],
                 leds: list[led_module.LED],
                 switches: list[switch_module.Switch],
                 vehicle: vehicle_module.Vehicle,
                 ):

        self.camera = camera
        self.distance_sensors = distance_sensors
        self.leds = leds
        self.switches = switches
        self.vehicle = vehicle

        self.running = True
        self.sample_hz = config['sample_hz']
        self.loop_counter = 0

    def logic(self):
        """Process sensor data, tell the vehicle how to drive"""
        pass

    def run(self):
        """The main loop of the Brain class. While running, and the switch is one, gather data from sensors and perform brain logic"""
        porcupine = pvporcupine.create(
  				access_key = PICOVOICE_KEY,
				#keywords=['picovoice', 'bumblebee']
  				keyword_paths=['../../../static/Hey-Fetcher_en_windows_v3_0_0.ppn']
		)
        while self.running:
            start_loop_time = time.time()

            self.camera.capture()
            self.logic()

            run_mic(porcupine, 1)
            transcript = language2UTF8()
            translated = translate_text('en', transcript)
            completion = gpt_query(translated)
            item = completion.choices[0].message.content
            print(item)
            detect("banana")

            # ensure that the loop is running at the correct max frequency
            time.sleep(max(0, 1/self.sample_hz -
                       (time.time() - start_loop_time)))

            self.loop_counter += 1
