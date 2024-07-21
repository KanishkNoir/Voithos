import streamlit as st
from mood import main as mood_tracker_main
from noteAgent import main as note_agent_main
from calendar_Tasks import main as calendar_tasks_main
from fitnessAgent import main as fitness_agent_main

def main():
    st.title("Student Multi-Agent System")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ['Home', 'Mood Tracker', 'Note Agent', 'Calendar'])
    page = st.sidebar.radio("Go to", ['Home', 'Mood Tracker', 'Study Buddy', 'Calendar', 'Fitness Buddy'])

    if page == 'Home':
        st.write("Welcome to the Student Multi-Agent System!")
        st.write("Use the sidebar to navigate to different features.")

    elif page == 'Mood Tracker':
        mood_tracker_main()

    elif page == 'Note Agent':
    elif page == 'Study Buddy':
        note_agent_main()
    
    elif page == 'Calendar':
        calendar_tasks_main()
    elif page == 'Fitness Buddy':
        fitness_agent_main()

if __name__ == "__main__":
    main()