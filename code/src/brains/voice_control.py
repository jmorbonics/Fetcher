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

def main():

	porcupine = pvporcupine.create(
  		access_key = PICOVOICE_KEY,
		#keywords=['picovoice', 'bumblebee']
  		keyword_paths=['../../../static/Hey-Fetcher_en_windows_v3_0_0.ppn']
	)

	
	run_mic(porcupine, 1)
	transcript = language2UTF8()
	translated = translate_text('en', transcript)
	completion = gpt_query(translated)
	item = completion.choices[0].message.content
	print(item)



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




if __name__ == "__main__":
    main()


