from transformers import pipeline

from ollamaHelper import init_responder, responder


init_responder()

while True:
    message = input("\n>")
    messages = [
    {"role": "system", "content": "You are a professinal translator. Tranlate the given language to english"},
    {"role": "user", "content": message},
]
    pipe = pipeline("text-generation", model="lightblue/suzume-llama-3-8B-multilingual")
    translated_message = pipe(messages)
    
    responder(translated_message)
    break
