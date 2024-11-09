import ollama 
import whisper
import speech_recognition as sr

from datetime import datetime, timedelta
from queue import Queue
from time import sleep

import pyaudio

def get_user_input():
    user_input = input("\n")
    return user_input

# Get audio from mic
whisper_model = whisper.load_model("tiny")

#Time when last phrase was retrieved from queue
phrase_time = None

# Queue to store audio data
data_queue = Queue()

recorder = sr.Recognizer()
recorder.energy_threshold = 1000
recorder.dynamic_energy_threshold = False

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

p.terminate
exit(1)
# List microphones
print(enumerate(sr.Microphone.list_microphone_names()))

microphone = input("\n")

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
            result = whisper_model.transcribe(audio_np, fp=torch.cuda.is_available(), device="cuda")
            text = result['text'].strip()

            if phrase_complete:
                transaciption.append(text)

            for line in transcription:
                    print(line)
            # Flush
            print('', end='', flush=True)
        else:
            sleep(0.25)
    except KeyboardInterrupt:
        break


#
# stream = ollama.chat(
#         model="responder",
#         messages=[{
#             'role': 'user',
#             'content': "**START CALL**"
#         }],
#         stream=True
#     )
#
#
# for chuck in stream:
#     print(chuck['message']['content'], end = "", flush=True)
#
#
# while True:
#     user_input = get_user_input()
#     stream = ollama.chat(
#             model="responder",
#             messages=[{
#                 'role': 'user',
#                 'content': user_input 
#             }],
#             stream=True
#     )
#     for chuck in stream:
#         print(chuck['message']['content'], end = "", flush=True)
#     
#     if user_input == "**END CALL**":
#         break
