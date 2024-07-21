import os
import streamlit as st
from together import Together
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=api_key)

def fitnessLLM(response, context):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "With a background in personal training and certification in strength and conditioning, you have a proven track record of helping clients build muscle, loose weight and improve their fitness levels. Your passion for fitness and dedication to personalized workout plans and support make you an invaluable part of the team."},
            {"role": "user", "content": f"Use the 'User's Details' as context to create a Personalized Workout Plan for client, based on the user's query: {response}. User's Details: {context}."}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
        
    st.write(collected_response)
    st.session_state['history'].append(f"\n{collected_response}")
    return collected_response

def nutritionLLM(response, context):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "With a degree in nutrition or dietetics and certification in your field, you have experience working with athletes and individuals with specific dietary needs. Your expertise includes meal planning, nutrient timing, and understanding the relationship between diet and exercise performance."},
            {"role": "user", "content": f"Use the 'User's Details' which include dietary needs and might also include fitness goals as context to tailor a customized Nutrition Plan for client, based on the user's query: {response}. User's Details: {context}."}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
        
    st.write(collected_response)
    st.session_state['history'].append(f"\n{collected_response}")
    return collected_response

def fitness_questionnaire():
    if 'user_fitness_res' not in st.session_state:
        st.session_state['user_fitness_res'] = None
        
    if st.session_state['user_fitness_res'] is None:   
        with st.expander("Fitness Questionnaire", expanded=True):
            st.write("Please answer all questions to generate your personalized fitness profile.")

            questions = [
            {
                "question": "What is your current fitness level?",
                "options": ["Beginner", "Intermediate", "Advanced"],
                "key": "fitness_level"
            },
            {
                "question": "What are your fitness goals?",
                "options": ["Weight loss", "Muscle gain", "Increased endurance", "Improved overall health"],
                "key": "fitness_goals"
            },
            {
                "question": "How many days per week can you dedicate to working out?",
                "options": [str(i) for i in range(1, 8)],
                "key": "workout_days"
            },
            {
                "question": "What time of day do you prefer to work out?",
                "options": ["Morning", "Afternoon", "Evening"],
                "key": "workout_time"
            },
            {
                "question": "Do you have any physical limitations or injuries that may impact your ability to perform certain exercises?",
                "key": "limitations"
            },
            {
                "question": "Are there any specific exercises or muscle groups you'd like to focus on?",
                "key": "focus_areas"
            },
            {
                "question": "Do you have access to a gym or would you prefer to work out at home?",
                "options": ["Gym", "Home", "Both"],
                "key": "workout_location"
            },
            {
                "question": "How much time are you willing to commit to each workout session?",
                "options": ["30 minutes", "45 minutes", "60 minutes"],
                "key": "workout_duration"
            },
            {
                "question": "Are you interested in incorporating any specific types of exercise into your routine?",
                "options": ["Cardio", "Strength training", "Flexibility exercises", "All of the above"],
                "key": "exercise_types"
            },
            {
                "question": "Do you have a preferred pace for your workouts?",
                "options": ["Fast-paced", "Moderate", "Slow and steady"],
                "key": "workout_pace"
            }
        ]

            responses = {}

            for q in questions:
                if "options" in q:
                    response = st.selectbox(q["question"], q["options"], key=q["key"])
                else:
                    response = st.text_input(q["question"], key=q["key"])

                responses[q["key"]] = response

            if st.button("Submit", key="fitness_questionnaire_btn"):
                if all(responses.values()):
                    st.session_state['user_fitness_res'] = responses
                    st.success("Thank you for completing the questionnaire!")
                    # st.json(responses)
                else:
                    st.error("Please answer all questions before submitting.")
    
    return st.session_state['user_fitness_res']

def nutriton_questionnaire():
    if 'user_nutrition_res' not in st.session_state:
        st.session_state['user_nutrition_res'] = None
        
    if st.session_state['user_nutrition_res'] is None:   
        with st.expander("Nutrition Questionnaire", expanded=True):
            st.write("Please answer all questions to generate your personalized diet plan.")

            questions = [
                {
                    "question": "What is your current diet type?",
                    "options": ["Omnivore", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo"],
                    "key": "diet_type"
                },
                {
                    "question": "What are your primary nutrition goals?",
                    "options": ["Weight loss", "Muscle gain", "Maintenance", "Improve overall health", "Manage a health condition"],
                    "key": "nutrition_goals"
                },
                {
                    "question": "How many meals do you typically eat per day?",
                    "options": ["2", "3", "4", "5 or more"],
                    "key": "meals_per_day"
                },
                {
                    "question": "Do you have any food allergies or intolerances?",
                    "key": "food_allergies"
                },
                {
                    "question": "How would you rate your current water intake?",
                    "options": ["Low (less than 4 cups per day)", "Moderate (4-8 cups per day)", "High (more than 8 cups per day)"],
                    "key": "water_intake"
                },
                {
                    "question": "Are you interested in meal planning and prep?",
                    "options": ["Yes, very interested", "Somewhat interested", "Not interested"],
                    "key": "meal_planning_interest"
                }
            ]

            responses = {}

            for q in questions:
                if "options" in q:
                    response = st.selectbox(q["question"], q["options"], key=q["key"])
                else:
                    response = st.text_input(q["question"], key=q["key"])

                responses[q["key"]] = response

            if st.button("Submit", key="nutrition_questionnaire_btn"):
                if all(responses.values()):
                    st.session_state['user_nutrition_res'] = responses
                    st.success("Thank you for completing the questionnaire!")
                    # st.json(responses)
                else:
                    st.error("Please answer all questions before submitting.")
    
    return st.session_state['user_nutrition_res']

def getFitnessAdvise(prompt, history, context):
    messages = [{"role": "user", "content": p} for p in history]
    messages.append({"role": "user", "content": prompt})

    try:
        responseLLM = fitnessLLM(prompt, context)
        return responseLLM
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    
def getNutritionAdvise(prompt, history, context):
    messages = [{"role": "user", "content": p} for p in history]
    messages.append({"role": "user", "content": prompt})

    try:
        responseLLM = nutritionLLM(prompt, context)
        return responseLLM
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

if 'history' not in st.session_state:
    st.session_state['history'] = []

def main():
    st.title("Fitness Buddy")
    st.markdown("""
        ## How to Use:
            1. Fill out the fitness questionnaire.
            2. Ask your personal trainer any fitness-related questions.
            3. View your personalized advice and workout plans.
    """)
    
    tab1, tab2 = st.tabs(["Fitness", "Nutrition"])

    with tab1:
        st.header("Get your personalized fitness regime.")
        fitness_questionnaire()
        user_fitness_res = st.session_state['user_fitness_res']
        
        if user_fitness_res is not None:
            with st.chat_message(name="user"):
                prompt = st.text_input("Ask anything to your personal trainer?")
            with st.chat_message(name="ai"): 
                if st.button("Submit Query", key="fitness_btn"):
                    if prompt:
                        with st.spinner('Processing...'):
                            st.session_state['history'].append(prompt)
                            response = getFitnessAdvise(prompt, st.session_state['history'], user_fitness_res)
                            if response:
                                st.session_state['history'].append(response)
                                st.success("Response received:")
                                st.write(response)
                            else:
                                st.error("Failed to get a response. Please try again.")

                    else:
                        st.error("Please enter a topic or question.")
        else:
            st.info("Please complete the fitness questionnaire above to get started.")
            
    with tab2:
        st.header("Let's create a nutrition plan just for your needs!")
        nutriton_questionnaire()
        user_nutrition_res = st.session_state['user_nutrition_res']
        
        if user_nutrition_res is not None:
            with st.chat_message(name="user"):
                prompt = st.text_input("Ask anything to your personal nutritionist?")
            with st.chat_message(name="ai"): 
                if st.button("Submit Query", key="nutrition_btn"):
                    if prompt:
                        with st.spinner('Processing...'):
                            st.session_state['history'].append(prompt)
                            response = getNutritionAdvise(prompt, st.session_state['history'], [user_nutrition_res, user_fitness_res])
                            if response:
                                st.session_state['history'].append(response)
                                st.success("Response received:")
                                st.write(response)
                            else:
                                st.error("Failed to get a response. Please try again.")

                    else:
                        st.error("Please enter a topic or question.")
        else:
            st.info("Please complete the nutrition questionnaire above to get started.")
            
    st.markdown("""
        ## How to Use:
            1. Fill out the fitness questionnaire.
            2. Ask your personal trainer any fitness-related questions.
            3. View your personalized advice and workout plans.
    """)
    
if __name__ == "__main__":
    main()