import asyncio
import cv2
import time
import os
import shutil
import threading
import warnings
import whisper
import speech_recognition as sr
import numpy as np
import torch
import json
from datetime import datetime, timedelta
from queue import Queue
from PIL import Image, ImageTk
from text import transliterate_text
from text_to_speech import text_to_speech
from ollamaHelper import init_responder, image_responder, responder, clear_messages
from threatHelper import init_threat_responder, threat_responder

class VideoHandler:
    def __init__(self):
        self.is_running = False
        self.cap = None
        self.video_thread = None
        self.audio_thread = None
        self.frame_label = None
        self.output_dir = "captured_frames"
        self._lock = threading.Lock()
        
        # Audio components
        self.data_queue = Queue()
        self.recorder = None
        self.stop_listening = None
        self.whisper_model = None
        
        # Ticket components
        self.user_id = ""
        self.ticket = {}
        
    def start_video(self, frame_label):
        if self.is_running:
            return False
            
        # Generate user ID and initialize ticket
        self.user_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
        self.ticket = {self.user_id: []}  # Changed to match ticket_log.json format
            
        # Set up output directory
        if os.path.exists(self.output_dir) and os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            return False
            
        self.frame_label = frame_label
        self.is_running = True
        
        # Initialize audio components
        self._setup_audio()
        
        # Initialize ollama and threat responder
        clear_messages()
        init_responder()
        init_threat_responder()
        
        # Start video and audio threads
        self.video_thread = threading.Thread(target=self._video_process)
        self.audio_thread = threading.Thread(target=self._audio_process)
        self.video_thread.daemon = True
        self.audio_thread.daemon = True
        self.video_thread.start()
        self.audio_thread.start()
        
        return True
        
    def _setup_audio(self):
        warnings.filterwarnings("ignore", category=UserWarning)
        torch.set_warn_always(False)

        self.whisper_model = whisper.load_model("base")
        
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = 1000
        self.recorder.dynamic_energy_threshold = False

        source = sr.Microphone(sample_rate=16000)
        with source:
            self.recorder.adjust_for_ambient_noise(source)

        self.stop_listening = self.recorder.listen_in_background(
            source, 
            self._audio_callback, 
            phrase_time_limit=5
        )
        
    def _audio_callback(self, _, audio: sr.AudioData) -> None:
        if self.is_running:
            data = audio.get_raw_data()
            self.data_queue.put(data)
        
    def stop_video(self):
        with self._lock:
            if not self.is_running:
                return
                
            self.is_running = False
            
            if self.stop_listening:
                self.stop_listening(wait_for_stop=False)
            
            if threading.current_thread() != self.video_thread:
                if self.video_thread:
                    self.video_thread.join(timeout=1.0)
            if threading.current_thread() != self.audio_thread:
                if self.audio_thread:
                    self.audio_thread.join(timeout=1.0)
            
            if self.cap and self.cap.isOpened():
                self.cap.release()
            
            self.data_queue.queue.clear()
            cv2.destroyAllWindows()
            print("\n\n Video and Audio stopped \n\n")
            
            # Save final ticket state if there are any threats
            if self.ticket[self.user_id]:
                try:
                    # Load existing tickets if any
                    if os.path.exists("ticket_log.json"):
                        with open("ticket_log.json", "r") as f:
                            existing_tickets = json.load(f)
                            existing_tickets.update(self.ticket)
                    else:
                        existing_tickets = self.ticket

                    with open("ticket_log.json", "w") as f:
                        json.dump(existing_tickets, f, indent=2)
                except Exception as e:
                    print(f"Error saving ticket: {e}")
                    
            self.ticket = {}
    
    def _audio_process(self):
        print("\n\n Audio Recording started \n\n")
        phrase_time = None
        phrase_timeout = 3
        
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

                    result = self.whisper_model.transcribe(audio_np)
                    text = result['text'].strip()

                    if phrase_complete and len(text) > 0:
                        print("\n**  "+text+"  **", flush=True)
                        val = responder(f"[VIDEO CALL] {text}")
                        if val[0] == False:
                            self.stop_video()
                            break

                        tranliterated_text = transliterate_text(val[1])
                        text_to_speech(tranliterated_text)
                        
                        # Process threat and update ticket
                        threat = asyncio.run(threat_responder(text))
                        if threat[0] == True:
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                            ticket_entry = {
                                "type": "video_audio_threat",
                                "timestamp": current_time,
                                "message": text,
                                "details": threat[1]
                            }
                            self.ticket[self.user_id].append(ticket_entry)
                            
                            try:
                                # Load existing tickets if any
                                if os.path.exists("ticket_log.json"):
                                    with open("ticket_log.json", "r") as f:
                                        existing_tickets = json.load(f)
                                        existing_tickets.update(self.ticket)
                                else:
                                    existing_tickets = self.ticket

                                with open("ticket_log.json", "w") as f:
                                    json.dump(existing_tickets, f, indent=2)
                                    
                                # print("******** TICKET:", self.ticket[self.user_id], "********")
                            except Exception as e:
                                print(f"Error saving ticket: {e}")
                                
                else:
                    time.sleep(0.25)
            except Exception as e:
                print(f"Error in audio processing: {e}")
                continue
        
    def _video_process(self):
        print("\n\n Video started \n\n")
        frame_interval = 1.0
        last_saved_time = time.time()
        frame_count = 0
        last_process_time = time.time()
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Failed to grab frame")
                    continue
                    
                # Update the GUI with the current frame
                if self.frame_label is not None:
                    try:
                        frame = cv2.resize(frame, (400, 300))
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                        imgtk = ImageTk.PhotoImage(image=img)
                        self.frame_label.after(0, self._update_label, imgtk)
                    except Exception as e:
                        print(f"Error updating frame: {e}")
                        continue
                
                current_time = time.time()
                if current_time - last_saved_time >= frame_interval:
                    try:
                        frame_filename = os.path.join(self.output_dir, f"frame_{frame_count}.jpg")
                        cv2.imwrite(frame_filename, frame)
                        frame_count += 1
                        last_saved_time = current_time
                        
                        if frame_count % 20 == 0 and (current_time - last_process_time) >= 5.0:
                            image_path = f"./{self.output_dir}/frame_{frame_count-1}.jpg"
                            
                            try:
                                response = asyncio.run(image_responder([image_path]))
                                last_process_time = current_time
                                
                                if "[THREAT]" in response:
                                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                                    ticket_entry = {
                                        "type": "video_visual_threat",
                                        "timestamp": current_time,
                                        "frame": image_path,
                                        "details": response
                                    }
                                    self.ticket[self.user_id].append(ticket_entry)
                                    
                                    try:
                                        # Load existing tickets if any
                                        if os.path.exists("ticket_log.json"):
                                            with open("ticket_log.json", "r") as f:
                                                existing_tickets = json.load(f)
                                                existing_tickets.update(self.ticket)
                                        else:
                                            existing_tickets = self.ticket

                                        with open("ticket_log.json", "w") as f:
                                            json.dump(existing_tickets, f, indent=2)
                                            
                                        print("******** VIDEO TICKET:", self.ticket[self.user_id], "********")
                                    except Exception as e:
                                        print(f"Error saving ticket: {e}")
                                    
                            except Exception as e:
                                print(f"Error in image processing: {e}")
                                
                    except Exception as e:
                        print(f"Error saving frame: {e}")
                        continue
                
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Error in video processing: {e}")
        finally:
            with self._lock:
                if self.cap and self.cap.isOpened():
                    self.cap.release()
                cv2.destroyAllWindows()
                
    def _update_label(self, imgtk):
        if self.frame_label and self.is_running:
            self.frame_label.imgtk = imgtk
            self.frame_label.configure(image=imgtk)