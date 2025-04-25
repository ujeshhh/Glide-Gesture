import streamlit as st
import subprocess
import psutil
import os
import time

# Paths to the scripts (modify if they are in a different directory)
GAME_SCRIPT_PATH = "main.py"
GESTURE_SCRIPT_PATH = "gesture.py"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🤖 Welcome to the Chatbot! Type a command or say hi! Available commands: 'open game', 'close game', 'open mouse and keyboard', 'close mouse and keyboard', 'help'"}
    ]
if "processes" not in st.session_state:
    st.session_state.processes = {
        "game": None,
        "gesture": None
    }

def run_script(script_path, process_key):
    """Run a Python script and store its process."""
    if not os.path.exists(script_path):
        return f"❌ Error: {script_path} not found."
    if st.session_state.processes[process_key] and psutil.pid_exists(st.session_state.processes[process_key].pid):
        return f"⚠️ {process_key} is already running."
    try:
        process = subprocess.Popen(["python", script_path])
        st.session_state.processes[process_key] = process
        return f"✅ Started {script_path} (PID: {process.pid})"
    except Exception as e:
        return f"❌ Error starting {script_path}: {e}"

def terminate_script(process_key):
    """Terminate a running script by its process."""
    if not st.session_state.processes[process_key] or not psutil.pid_exists(st.session_state.processes[process_key].pid):
        return f"⚠️ {process_key} is not running."
    try:
        parent = psutil.Process(st.session_state.processes[process_key].pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        time.sleep(0.5)
        if psutil.pid_exists(st.session_state.processes[process_key].pid):
            parent.kill()
        st.session_state.processes[process_key] = None
        return f"✅ Terminated {process_key}"
    except Exception as e:
        return f"❌ Error terminating {process_key}: {e}"

def handle_command(user_input):
    """Process user input and return a response."""
    user_input = user_input.lower().strip()

    # Basic greetings and commands
    greetings = {
        "hi": "👋 Hi there!",
        "hello": "👋 Hello! How can I assist you?",
        "how are you": "😄 I'm doing great, thanks for asking! How about you?",
        "bye": "👋 Goodbye! Type 'help' if you need me again!",
        "help": "ℹ️ Available commands: 'open game', 'close game', 'open mouse and keyboard', 'close mouse and keyboard'. You can also say 'hi', 'hello', 'how are you', or 'bye'."
    }

    if user_input in greetings:
        return greetings[user_input]

    # Script execution commands
    if user_input == "open game":
        return run_script(GAME_SCRIPT_PATH, "game")
    elif user_input == "close game":
        return terminate_script("game")
    elif user_input == "open mouse and keyboard":
        return run_script(GESTURE_SCRIPT_PATH, "gesture")
    elif user_input == "close mouse and keyboard":
        return terminate_script("gesture")
    else:
        return "❓ Unknown command. Try 'open game', 'close game', 'open mouse and keyboard', 'close mouse and keyboard', or say 'hi', 'hello', 'how are you', 'bye', or 'help'."

# Streamlit app layout
st.title("🤖 Game Control Chatbot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for user commands
user_input = st.chat_input("Type your command or say hi...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get and add assistant response
    response = handle_command(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update the UI
    st.rerun()