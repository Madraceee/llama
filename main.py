from autogen import AssistantAgent, UserProxyAgent

config_responder = [
  {
    "model": "responder",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
  },
]

assistant = AssistantAgent("assistant", llm_config={"config_list": config_responder})

user_proxy_agent = UserProxyAgent("user_proxy", human_input_mode = "ALWAYS", llm_config=False)
user_proxy_agent.initiate_chat(assistant, message="who are you?")

# assistant.receive(message="**START**", sender = user_proxy_agent, request_reply = True)
reply = assistant.reply(message="**START**")

while True:
    print(reply)
    user_proxy_agent.get_human_input("temp")
    break
