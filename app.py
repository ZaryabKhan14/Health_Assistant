from datetime import datetime

import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("api_key")

# Initialize OpenAI client
client = openai.Client(api_key=api_key)

# Function to handle the chat with the assistant
def assistant_chatbot(user_query, thread_id=None):
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id
    else:
        thread_id = thread_id

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_query,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id="asst_6o7w7E8I6m0cVfM3zFzePcb9",
        instructions="Provide information related to health queries. Remember, this is not medical advice. For serious health concerns, consult a healthcare professional.",
    )

    # Wait for the run to complete
    while not run.completed_at:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    last_message = messages.data[0]
    response = last_message.content[0].text.value

    return response, thread_id

# Streamlit app layout and logic
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None



# Streamlit app layout
st.title("Health Assistant Chatbot")
st.sidebar.write("Ask any health-related questions. (This is not medical advice.)")

# Persistent state for messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

user_query = st.sidebar.text_input("Enter your health query:", key="query")

if st.sidebar.button("Submit"):
    if user_query.strip():
        response, thread_id = assistant_chatbot(user_query, st.session_state['thread_id'])
        st.session_state['thread_id'] = thread_id
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['messages'].append((timestamp, "User", user_query))
        st.session_state['messages'].append((timestamp, "Bot", response))

if st.sidebar.button("Clear Chat"):
    st.session_state['messages'] = []

# Chat container
chat_container = st.container()
with chat_container:
    for timestamp, role, message in st.session_state['messages']:
        st.markdown(f"**{timestamp} {role}**: {message}")

st.sidebar.markdown("---")
if st.sidebar.button("Export Chat"):
    st.session_state['messages'] = []
st.sidebar.write("Disclaimer: This chatbot provides information, not medical advice.")