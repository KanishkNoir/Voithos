import os
import streamlit as st
from datetime import datetime
from PIL import Image
from together import Together
from dotenv import load_dotenv

load_dotenv()

# Set up the Together API client
api_key = os.getenv('TOGETHER_API_KEY')  # Ensure this environment variable is set
client = Together(api_key=api_key)


def get_llama_response(prompt, max_tokens=512):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
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
        return "Sorry, something went wrong. Please try again later."


# Initialize session state for selected mood, user data, and recommendations
if 'selected_mood' not in st.session_state:
    st.session_state['selected_mood'] = None

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}

if 'show_more' not in st.session_state:
    st.session_state['show_more'] = False

if 'initial_recommendations' not in st.session_state:
    st.session_state['initial_recommendations'] = ""

if 'additional_recommendations' not in st.session_state:
    st.session_state['additional_recommendations'] = ""


# Function to log mood
def log_mood(mood):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if mood not in st.session_state['user_data']:
        st.session_state['user_data'][mood] = []
    st.session_state['user_data'][mood].append(date_str)


# Function to display mood selection
def mood_selection():
    st.write("### How are you feeling today?")
    mood_image_path = "moo.png"  # Update the path to the uploaded image
    mood_image = Image.open(mood_image_path)
    mood_width, mood_height = mood_image.size
    num_moods = 5
    mood_slice_width = mood_width // num_moods

    mood_labels = ["awful", "bad", "meh", "good", "rad"]
    mood_images = {label: mood_image.crop((i * mood_slice_width, 0, (i + 1) * mood_slice_width, mood_height)) for
                   i, label in enumerate(mood_labels)}

    cols = st.columns(len(mood_images))
    for idx, (mood, img) in enumerate(mood_images.items()):
        with cols[idx]:
            if st.button(mood):
                st.session_state['selected_mood'] = mood
                log_mood(mood)
                st.session_state['initial_recommendations'] = ""  # Reset recommendations when mood changes
                st.session_state['additional_recommendations'] = ""
                st.session_state['show_more'] = False
            st.image(img, caption=mood)


# Function to get personalized recommendations
def personalized_recommendations(mood, more=False):
    if more:
        prompt = f"Hey there! I'm still feeling quite {mood}. Can you suggest 3 more fun and relaxing activities to help improve this mood and boost productivity different from the prev ones u suggested?"
    else:
        prompt = f"Hey there! I'm feeling quite {mood}. Can you suggest 3 fun and relaxing activities I can do right now to help improve this mood and boost productivity? these may include accupresure points, or specific breathing or stretches if you have any sometimes. Please keep them concise. If the {mood} is good or rad, can you start off along these lines pls: I’m glad that you’re doing good! Here are some exercises to keep your mood regulated throughout the day!"

    recommendations = get_llama_response(prompt, max_tokens=150 if more else 512)
    return recommendations


# Function to display images for recommendations
def display_recommendation_images(recommendations):
    # Placeholder images for the recommendations
    images = {
        "30 sec downtime": "https://via.placeholder.com/150?text=30+Sec+Downtime",
        "2 min downtime": "https://via.placeholder.com/150?text=2+Min+Downtime",
        "Eye stretch": "https://via.placeholder.com/150?text=Eye+Stretch",
        "Acupressure points": "https://via.placeholder.com/150?text=Acupressure+Points"
    }

    recommendations_list = recommendations.split('\n')
    formatted_recommendations = ""
    for rec in recommendations_list:
        if rec.strip():
            formatted_recommendations += f"<div style='margin-bottom: 10px;'>{rec}</div>"

    st.markdown(formatted_recommendations, unsafe_allow_html=True)

# Initialize session state variables
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}

if 'selected_mood' not in st.session_state:
    st.session_state['selected_mood'] = None
    
# Define the main page
def main():
    st.title("Mood Check!")
    st.write("Select your current mood to get personalized recommendations to improve your mood and boost productivity.")

    mood_selection()
    selected_mood = st.session_state.get('selected_mood', None)

    if selected_mood:
        st.write(f"### Selected Mood: {selected_mood}")

        if not st.session_state['initial_recommendations']:
            st.session_state['initial_recommendations'] = personalized_recommendations(selected_mood)

        st.write("## Recommendations")
        display_recommendation_images(st.session_state['initial_recommendations'])

        if st.button("Show more activities"):
            st.session_state['show_more'] = True

        if st.session_state['show_more']:
            if not st.session_state['additional_recommendations']:
                st.session_state['additional_recommendations'] = personalized_recommendations(selected_mood, more=True)
            display_recommendation_images(st.session_state['additional_recommendations'])


# Add some CSS for styling
st.markdown(
    """
    <style>
    .stButton button {
        background-color: white;
        color: black;
        border-radius: 12px;
        border: 1px solid #ccc;
    }
    .stButton button:hover {
        background-color: #ADD8E6;
        color: black;
        border: 1px solid #0000FF; /* Blue border on hover */
    }
    .stImage img {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()