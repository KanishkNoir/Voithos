# Overview
Developed a system to process student queries and classify them into one or more categories: scheduler, wellness, diet, and note maker. Based on the classification, the system generates a tailored prompt for each category. If a query falls into multiple categories, the system creates separate prompts for each relevant category and sends them to the respective agents. Each agent processes its prompt and returns an output. The system then aggregates these outputs into a single, comprehensive response, ensuring the student receives all necessary information and tasks are completed efficiently in one go.

# Agent Processing
## Scheduler Agent
  Handles calendar-related queries.
  Interacts directly with the Google Calendar API to manage events and schedules.
  Focuses on efficient API interactions without using RAG (Retrieval-Augmented Generation).
  
## Note Maker Agent
  Manages study notes and creates study materials.
  Uses RAG for generating quizzes, flashcards, and mindmaps ensuring contextually relevant content.
  Interacts with a dedicated note storage system for basic note management.
  Here is the RAG pipeline used in this app:
  <img width="537" alt="image" src="https://github.com/user-attachments/assets/b64b29ac-e02b-4076-b4ca-3ff43c962967">

## Fitness Agent
  Provides workout schedules and mental health advice.
  Uses predefined plans and resources without RAG.
  Potential future integration with external fitness tracking APIs.
  
## Mood Agent
  Emotional Support: Provide empathetic responses and comforting messages to help users manage their emotions and feel understood.
  Mood Tracking: Enable users to log and monitor their mood over time, offering insights and trends to help them understand their emotional patterns.
  Coping Strategies: Suggest personalized coping mechanisms and activities, such as breathing exercises, mindfulness practices to help users improve their mood.

# Running the application 
Follow these steps to run the application:

1. **Clone the Repository**
   ```
   git clone https://github.com/jaz404/llama3hackathon.git
   ```
2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```
3. **Run the Application**
   ```
   streamlit run app.py
   ```
4. **Access the Application**
  Open your web browser and navigate to the address provided by Streamlit usually ```http://localhost:8501```
