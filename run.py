import asyncio
import warnings
import ollama 
import whisper
import speech_recognition as sr
import numpy as np
import torch
import json
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
import pyaudio
from text import transliterate_text
from text_to_speech import text_to_speech
from ollamaHelper import init_responder, responder
from threatHelper import init_threat_responder, threat_responder

# Filter out warnings
warnings.filterwarnings("ignore", category=UserWarning)
# Specifically for PyTorch warnings
torch.set_warn_always(False)

def get_user_input():
    user_input = input("\n")
    return user_input

# Load Whisper
whisper_model = whisper.load_model("small")

#Time when last phrase was retrieved from queue
phrase_time = None

# Queue to store audio data
data_queue = Queue()

recorder = sr.Recognizer()
recorder.energy_threshold = 1000
recorder.dynamic_energy_threshold = False

mic_name = "default"

source=sr.Microphone(sample_rate=16000)


with source:
    recorder.adjust_for_ambient_noise(source)

def callback_record(_,audio: sr.AudioData) -> None:
    data = audio.get_raw_data()
    data_queue.put(data)

recorder.listen_in_background(source, callback_record, phrase_time_limit=5)

phrase_timeout = 3
transcription = ['']

print("\n\n Recording started \n\n")
threat_response = init_threat_responder()
initial_response = init_responder()
if initial_response[0]:  # If successful
    text_to_speech(initial_response[1])

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

            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            options = whisper.DecodingOptions()
            result = whisper_model.transcribe(audio_np)
            text = result['text'].strip()

            if phrase_complete and len(text) > 0:
                print("\n**  "+text+"  **", flush=True)
                val = responder(text)
                if val[0] == False:
                    # process_threat_tickets()  # Process any final tickets before breaking
                    break

                tranliterated_text = transliterate_text(val[1])
                text_to_speech(tranliterated_text)
                threat = asyncio.run(threat_responder(text))

            print('', end='', flush=True)
            
        else:
            sleep(0.25)
    except KeyboardInterrupt:
        break
