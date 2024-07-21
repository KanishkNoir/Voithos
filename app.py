import streamlit as st
from mood import main as mood_tracker_main
# from noteAgent import main as note_agent_main
from calendar_Tasks import main as calendar_tasks_main
from fitnessAgent import main as fitness_agent_main
import os
from together import Together

def classify_query(query):
    client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
    messages = [
        {"role": "system", "content": "You are a helpful assistant that classifies user queries into categories: 'Mood Tracker', 'Study Buddy', 'Calendar', or 'Fitness Buddy'. Respond with only the category name."},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        messages=messages,
        max_tokens=10,
        temperature=0.3,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>"],
    )
    return response.choices[0].message.content.strip()

def main():
    st.title("Student Multi-Agent System")
    # Enhanced Custom CSS for improved aesthetics
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f0f2f6;
        color: #1e1e1e;
    }
    .description {
        font-size: 32px;
    }
    .title {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 30px;
        color: #fff;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 28px;
        font-weight: 400;
        margin-bottom: 15px;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    .section {
        margin-top: 40px;
        margin-bottom: 40px;
        background-color: #36454F;
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature {
        font-size: 18px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    # Sidebar for navigation
    st.sidebar.title("Student Portal")
    if st.sidebar.button('Home'):
        st.session_state.page = 'Home'
    if st.sidebar.button('Mood Tracker'):
        st.session_state.page = 'Mood Tracker'
    if st.sidebar.button('Study Buddy'):
        st.session_state.page = 'Study Buddy'
    if st.sidebar.button('Calendar'):
        st.session_state.page = 'Calendar'
    if st.sidebar.button('Fitness Buddy'):
        st.session_state.page = 'Fitness Buddy'

    if page == 'Home':
        st.write("Welcome to the Student Multi-Agent System!")
        st.write("Use the sidebar to navigate to different features.")
    if st.session_state.page == 'Home':
        st.markdown('<p class="title">🎓 Welcome to the Student Multi-Agent System!</p>', unsafe_allow_html=True)
        st.write('<p class="description">Your all-in-one platform for managing your student life.</p>', unsafe_allow_html=True)

    elif page == 'Mood Tracker':
        mood_tracker_main()
        st.markdown('<p class="subtitle section">How can I help you today?</p>', unsafe_allow_html=True)
        user_query = st.text_input("Enter your task or question:")
        
        if user_query:
            with st.spinner("Analyzing your request..."):
                classified_page = classify_query(user_query)
            
            st.success(f"Based on your query, I think you want to use the {classified_page} feature.")
            if st.button(f"Go to {classified_page}"):
                st.session_state.page = classified_page
                st.experimental_rerun()

        st.markdown('<p class="subtitle section">🚀 Why this project?</p>', unsafe_allow_html=True)
        st.write("""
        The Student Multi-Agent System was created to address the unique challenges faced by students in managing their academic and personal lives. Our goal is to provide a comprehensive tool that:

    elif page == 'Note Agent':
    elif page == 'Study Buddy':
        1. Helps students track their emotional well-being
        2. Assists in organizing and managing notes effectively
        3. Streamlines calendar management for better time allocation

        By integrating these essential features into one platform, we aim to enhance students' productivity and overall college experience.
        """)

        st.markdown('<p class="subtitle section">✨ Features</p>', unsafe_allow_html=True)
        st.write("Use the sidebar to navigate to different features:")
        st.markdown('<p class="feature">• 😊 <b>Mood Tracker</b>: Monitor your emotional well-being</p>', unsafe_allow_html=True)
        st.markdown('<p class="feature">• 📝 <b>Study Buddy</b>: Organize and manage your study notes</p>', unsafe_allow_html=True)
        st.markdown('<p class="feature">• 📅 <b>Calendar</b>: Keep track of your schedules and deadlines</p>', unsafe_allow_html=True)
        st.markdown('<p class="feature">• 💪 <b>Fitness Buddy</b>: Stay on top of your fitness goals</p>', unsafe_allow_html=True)

        # Rest of the home page content...

    elif st.session_state.page == 'Mood Tracker':
        mood_tracker_main()
    elif st.session_state.page == 'Study Buddy':
        note_agent_main()
    
    elif page == 'Calendar':
        calendar_tasks_main()
    elif page == 'Fitness Buddy':
        fitness_agent_main()

if __name__ == "__main__":
    main()
