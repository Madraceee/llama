from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# Configuration for Ollama
def get_ollama_config():
    config_list = [{
        "model": "responder:latest",  # Your custom model name in Ollama
        "base_url": "http://localhost:11434/v1",  # Default Ollama API endpoint
        "api_type": "ollama",
    }]
    return config_list

# Create the agent configuration
agent_config = {
    "seed": 42,  # For reproducibility
    "temperature": 0.0,
    "config_list": get_ollama_config(),
    "request_timeout": 120,
}

# Create the 911 responder agent
responder = AssistantAgent(
    name="911_responder",
    system_message="You are a 911 responder agent. You are deployed in an actual station and you will get actual calls from humans in distress. Do not make this into a chat session. DO NOT MAKE STORIES. You will respond to actual emergencies.",
    llm_config=agent_config
)

# Create a user proxy agent
user = UserProxyAgent(
    name="caller",
    code_execution_config=False  # Disable code execution for safety
)

# Function to check if Ollama is running
def check_ollama_connection():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except Exception:
        return False

# Example usage
if __name__ == "__main__":
    if not check_ollama_connection():
        print("Error: Ollama is not running. Please start Ollama first.")
    else:
        # Start the conversation
        user.initiate_chat(
            responder,
            message="This is a test emergency call."
        )
