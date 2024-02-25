from typing import TypedDict
#from .. voice_control import run_mic, language2UTF8, gpt_query
#from yolo_opencv_fetcher import detect, get_output_layers, draw_prediction
from .. import vehicle as vehicle_module, camera as camera_module, distance_sensor as distance_sensor_module, led as led_module, switch as switch_module
import time
#import pyaudio
import numpy as np
import os
# import pvporcupine
# from pvrecorder import PvRecorder
# import wave
# import struct
# from google.cloud import speech_v1p1beta1 as speech
# import openai
# from openai import OpenAI
from dotenv import load_dotenv

# CHUNK_SIZE = 512
# #FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../fetcher-415315-deae76a1ddb7.json"
# load_dotenv()
# OPENAI_KEY = os.getenv("OPENAI_API_KEY")
# PICOVOICE_KEY = os.getenv("PICOVOICE_API_KEY")


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


def run_mic(porcupine, index):
	recorder = PvRecorder(
		frame_length = porcupine.frame_length,
		device_index = index
	)
	recorder.start()
	print("Recording ...")
	while True:
		try:
			pcm = recorder.read()
			keyword_index = porcupine.process(pcm)

			if keyword_index >= 0:
				print("keyword detected")

				
				wavfile = wave.open("../../../static/question.wav", "w")
				wavfile.setparams((1, 2, recorder.sample_rate, 50, "NONE", "NONE"))

				for i in range(0, int(recorder.sample_rate / 512 * 4)):
					frame = recorder.read()
					wavfile.writeframes(struct.pack("h" * len(frame), *frame))

				wavfile.close()
				print("recording end")
				return

		except KeyboardInterrupt:
			print("Stopping...")
			return


def language2UTF8():
	client = speech.SpeechClient()
	speech_file = "../../../static/question.wav"
	first_lang = "en-US"

	with wave.open(speech_file, "rb") as wf:
	    sample_rate = wf.getframerate()

	with open(speech_file, "rb") as audio_file:
	    content = audio_file.read()

	audio = speech.RecognitionAudio(content=content)

	config = speech.RecognitionConfig(
	    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
	    sample_rate_hertz=sample_rate,
	    audio_channel_count=1,
	    language_code=first_lang,
	    alternative_language_codes=["es", "cmn-CN", "hi"],
	)

	print("Waiting for operation to complete...")
	response = client.recognize(config=config, audio=audio)

	for i, result in enumerate(response.results):
	    alternative = result.alternatives[0]
	    print("-" * 20)
	    print(f"First alternative of result {i}: {alternative}")
	    print(f"Transcript: {alternative.transcript}")

	return (response.results)[0].alternatives[0].transcript

def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result['translatedText']



def gpt_query(text):
	org = "Personal"
	key = OPENAI_KEY
	client = OpenAI(api_key = key)
	completion = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    	messages = [
			{
				"role": "system", 
				"content": "Parse sentence into a singular word for grocery item."
			},
			{
				"role": "user", 
				"content": text
			}
		],
	)
	return completion


def get_output_layers(net):
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h, COLORS, classes):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x-10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def detect(item):
    classes = None
    with open("yolov3.txt", 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

    # Initialize video capture from camera
    cap = cv2.VideoCapture(0)


    # main logic loop for aisle
    while True:
        ret, image = cap.read()
        if not ret:
            break

        Width = image.shape[1]
        Height = image.shape[0]
        scale = 0.00392

        blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)

        outs = net.forward(get_output_layers(net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        for i in indices:
            try:
                box = boxes[i]
            except:
                i = i[0]
                box = boxes[i]
            
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h), COLORS, classes)
            
            # print(str(classes[class_ids[i]]))
            # Check if the detected object is a banana
            if str(classes[class_ids[i]]) == item:
                cap.release()
                cv2.destroyAllWindows()
                return

        cv2.imshow("object detection", image)
        key = cv2.waitKey(1)
        if key == 27:  # Press ESC to exit
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

