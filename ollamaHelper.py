import ollama

def init_responder(shouldPrint=True):
    response = ollama.chat(
        model="responder",
        messages=[{
            'role': 'user',
            'content': "**START CALL**"
        }],
    )

    if shouldPrint:
        print(response['message']['content'], end = "", flush=True)

    return response['message']['content']


messages=[]
def responder(user_input, shouldPrint = True):
    messages.append({
                'role': 'user',
                'content': user_input 
            })
    response = ollama.chat(
            model="responder",
            messages=messages,
    )
    messages.append(response)
    if shouldPrint:
        print(response['message']['content'], end = "", flush=True)
    return response['message']['content']

def clear_messages():
    messages = []
