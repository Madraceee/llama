import threading
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

warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")
warnings.filterwarnings("ignore", category=UserWarning, module="whisper")

class AudioHandler:
    def __init__(self):
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)

        self.is_running = False
        self.data_queue = Queue()
        self.audio_thread = None
        self.recorder = None
        self.stop_listening = None
        self.user_id = ""
        self.ticket = {}
        
    def start_audio(self):
        if self.is_running:
            return
        
        self.user_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
        self.ticket[self.user_id] = []
        self.is_running = True
        self.audio_thread = threading.Thread(target=self._audio_process)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
    def stop_audio(self):
        if not self.is_running:
            return
            
        self.is_running = False
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        self.data_queue.queue.clear()
        
        # Save final ticket state if there are any threats
        if self.ticket[self.user_id]:
            with open("ticket_log.json", "w+") as f:
                json.dump(self.ticket, f, indent=2)
                
        self.ticket = {}
                                        
    def _audio_process(self):
        # Filter out warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        torch.set_warn_always(False)

        # Load Whisper
        whisper_model = whisper.load_model("base")
        phrase_time = None
        
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = 1000
        self.recorder.dynamic_energy_threshold = False

        source = sr.Microphone(sample_rate=16000)
        
        with source:
            self.recorder.adjust_for_ambient_noise(source)

        def callback_record(_, audio: sr.AudioData) -> None:
            if self.is_running:
                data = audio.get_raw_data()
                self.data_queue.put(data)

        self.stop_listening = self.recorder.listen_in_background(source, callback_record, phrase_time_limit=5)

        phrase_timeout = 3
        transcription = ['']
        
        print("\n\n Recording started \n\n")
        threat_response = init_threat_responder()
        initial_response = init_responder()
        if initial_response[0]:
            text_to_speech(initial_response[1])

        while self.is_running:
            try:
                now = datetime.utcnow()
                
                if not self.data_queue.empty():
                    phrase_complete = False
                    if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                        phrase_complete = True

                    phrase_time = now
                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()

                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                    result = whisper_model.transcribe(audio_np)
                    text = result['text'].strip()

                    if phrase_complete and len(text) > 0:
                        print("\n**  "+text+"  **", flush=True)
                        val = responder(text)
                        if val[0] == False:
                            self.stop_audio()
                            break

                        tranliterated_text = transliterate_text(val[1])
                        text_to_speech(tranliterated_text)
                        
                        # Process threat and update ticket
                        threat = asyncio.run(threat_responder(text))
                        if threat[0] == True:
                            # Format the ticket entry
                            ticket_entry = {
                                "type": "audio_threat",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                "message": text,
                                "details": threat[1]
                            }
                            self.ticket[self.user_id].append(ticket_entry)
                            
                            # Save ticket immediately
                            with open("ticket_log.json", "w+") as f:
                                json.dump(self.ticket, f, indent=2)
                            # print("******** TICKET:", self.ticket[self.user_id], "********")

                    print('', end='', flush=True)
                    
                else:
                    sleep(0.25)
            except Exception as e:
                print(f"Error in audio processing: {e}")
                break

        print("\n\n Recording stopped \n\n")