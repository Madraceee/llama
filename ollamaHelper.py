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


def responder(user_input):
    response = ollama.chat(
            model="responder",
            messages=[{
                'role': 'user',
                'content': user_input 
            }],
    )
    print(response['message']['content'], end = "", flush=True)
    
    if "**END CALL**" in response['message']['content']:
        return False
    return True
