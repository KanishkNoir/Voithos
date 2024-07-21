import os
import streamlit as st
from together import Together

# Set up the Together API client
api_key = os.environ.get('TOGETHER_API_KEY')  # Ensure this environment variable is set
client = Together(api_key=api_key)


def get_llama_response(prompt, history):
    messages = [{"role": "user", "content": p} for p in history]
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2,
            stop=None,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Initialize session state for conversation history
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 2rem;
        border-radius: 10px;
        color: black;
    }
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 10px;
    }
    .reportview-container .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# App title and subheader
st.title("Student Multi-Agent System")
st.subheader("An intelligent assistant for students")

# Sidebar content
st.sidebar.title("Input")
st.sidebar.write("Enter a prompt for the system:")

# Prompt input in the sidebar
prompt = st.sidebar.text_input("Prompt:")
if st.sidebar.button("Submit"):
    with st.spinner('Processing...'):
        if prompt:
            # Add user prompt to history
            st.session_state['history'].append(prompt)

            response = get_llama_response(prompt, st.session_state['history'])
            if response:
                # Add response to history
                st.session_state['history'].append(response)
                st.success("Response received:")
            else:
                st.error("Failed to get a valid response from the system.")
        else:
            st.error("Please enter a prompt.")

# Display conversation history
st.markdown("### Conversation ")
for i in range(0, len(st.session_state['history']), 2):
    st.markdown(f"**You:** {st.session_state['history'][i]}")
    if i + 1 < len(st.session_state['history']):
        st.markdown(f"**Assistant:** {st.session_state['history'][i + 1]}")

# Instructions or additional information in the main area
st.markdown("""
    ## How to Use
    1. Enter your query in the prompt box on the left sidebar.
    2. Click "Submit" to receive a response from the system.
    3. View the response in the main area.

    ## Examples
    - "Can you help me with calculus integration?"
    - "What’s on my schedule for today?"
    - "I need help studying for my biology exam."
""")

# Footer or additional links
st.markdown("""
    ---
    **Student Multi-Agent System** | Developed by [Your Name](https://your-website.com)
""")
