import asyncio
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

    return [True,response['message']['content']]


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

    if "**END CALL**" in response['message']['content']:
        return [False, response['message']['content']]
    return [True, response['message']['content']]

async def image_responder(images , shouldPrint = True):
    await asyncio.sleep(1)
    messages.append({
                'role': 'SYSTEM',
                'content': "The caller is sharing image feed while they are in distress, use this to update your knowledge base and describe the captured frames. I want you to also summarise what you see in the images and also what you hear from the caller.",
                'images': images
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
