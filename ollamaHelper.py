import ollama

def init_responder():
    stream = ollama.chat(
        model="responder",
        messages=[{
            'role': 'user',
            'content': "**START CALL**"
        }],
        stream=True
    )


    for chuck in stream:
        print(chuck['message']['content'], end = "", flush=True)


messages=[]
def responder(user_input):
    messages.append({
                'role': 'user',
                'content': user_input 
            })
    response = ollama.chat(
            model="responder",
            messages=messages,
    )
    messages.append(response)
    print(response['message']['content'], end = "", flush=True)
    
    if "**END CALL**" in response['message']['content']:
        return False
    return True
