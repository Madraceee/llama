import asyncio
import ollama
from queue import Queue
import json

threat_conversation = []

def init_threat_responder():
    # Initialize threat monitor with START marker
    threat_conversation = []
    ollama.chat(
        model="threat",
        messages=[{
            'role': 'user',
            'content': ""
        }]
    )

async def threat_responder(user_input):
    await asyncio.sleep(1)
    # Add caller's input to both conversations
    threat_conversation.append({
        'role': 'user',
        'content': user_input 
    })
    
    # Send complete conversation update to threat detector
    threat_response = ollama.chat(
        model="threat",
        messages=threat_conversation
    )
    
    # Format the conversation for threat monitoring
    threat_conversation.append(threat_response)
    
    # print("Threat Response:", threat_response['message']['content'], end="", flush=True)

    if "**END CALL**" in threat_response['message']['content']:
        threat_response_sent = [False]
        return threat_response_sent
    threat_response_sent = [True, threat_response['message']['content']]
    return threat_response_sent