import ollama 
import whisper
import speech_recognition as sr
import numpy as np
import torch

from datetime import datetime, timedelta
from queue import Queue
from time import sleep

import pyaudio

from ollamaHelper import init_responder, responder

def get_user_input():
    user_input = input("\n")
    return user_input

# Load Whisper
whisper_model = whisper.load_model("base")

#Time when last phrase was retrieved from queue
phrase_time = None

# Queue to store audio data
data_queue = Queue()

recorder = sr.Recognizer()
recorder.energy_threshold = 1000
recorder.dynamic_energy_threshold = False
 
# List microphones
# for name in  enumerate(sr.Microphone.list_microphone_names()):
#     print(name)

# mic_name = input("\n")
mic_name = "default"

for index, name in enumerate(sr.Microphone.list_microphone_names()):
    if mic_name in name:
        source = sr.Microphone(sample_rate=16000, device_index = index)
        break


with source:
    recorder.adjust_for_ambient_noise(source)

def callback_record(_,audio: sr.AudioData) -> None:
    data = audio.get_raw_data()
    data_queue.put(data)

recorder.listen_in_background(source, callback_record, phrase_time_limit=5)

phrase_timeout = 3
transcription = ['']


print("\n\n Recording started \n\n")
init_responder()
while True:
    try:
        now = datetime.utcnow()
        
        if not data_queue.empty():
            phrase_complete = False
            if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                phrase_complete = True

            phrase_time = now
            audio_data = b''.join(data_queue.queue)
            data_queue.queue.clear()

            # From net
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            #Transcribe
            options = whisper.DecodingOptions()
            result = whisper_model.transcribe(audio_np)
            text = result['text'].strip()

            if phrase_complete and len(text) > 0:
                print("**"+text+"**",flush=True)
                val = responder(text)
                if val == False:
                    break

            print('', end='', flush=True)
        else:
            sleep(0.25)
    except KeyboardInterrupt:
        break
