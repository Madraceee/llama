import asyncio
import ollama
from queue import Queue
import json

# # Queue to store threat tickets
# threat_tickets = Queue()

def init_threat_responder():
    # Initialize threat monitor with START marker
    ollama.chat(
        model="threat",
        messages=[{
            'role': 'user',
            'content': ""
        }]
    )

# messages = []
threat_conversation = []

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
        return False
    return True

# def get_threat_tickets():
#     """
#     Retrieve all available threat tickets from the queue.
#     Returns a list of threat tickets.
#     """
#     tickets = []
#     while not threat_tickets.empty():
#         tickets.append(threat_tickets.get())
#     return tickets