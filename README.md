# llama3hackathon

Develop a system that processes a student’s query and classifies it into one or more of the following categories: scheduler, wellness, diet, note maker. Based on the classification, the system generates a new prompt tailored to each category. If a query falls into multiple categories, the system creates separate prompts for each relevant category and sends them to their respective agents. Each agent processes its prompt and returns an output. The system then aggregates these outputs into a single, comprehensive response, ensuring the student receives all necessary information and tasks are completed efficiently in one go.

Query Intake:

The system receives a query from the student through a frontend interface (Streamlit in your case).


Query Processing:

The main process in main.py takes this query and initiates the CrewAI workflow.


CrewAI Orchestration:

CrewAI manages the sequence of operations, determining which agents should handle the query based on its content.


Agent Processing:

Scheduler Agent:

Handles calendar-related queries.
Interacts directly with the Google Calendar API to manage events and schedules.
It doesn't use RAG, focusing on efficient API interactions.


Note Maker Agent:

Manages study notes and creates study materials.
Uses RAG for generating quizzes and flashcards, ensuring contextually relevant content.
Interacts with a dedicated note storage system for basic note management.


Fitness Agent:

Provides customized workout plans based on user's needs.
Users need to answer some simple questions to get customized workout plans and tips
Currently, it uses pre-trained data and resources without RAG.

Future Scope: Could integrate with external fitness tracking APIs in the future.


Diet Agent:

Offers diet recommendations and nutritional guidance.
Utilizes RAG to provide up-to-date and varied nutritional advice.
Could integrate with nutritional databases or food tracking APIs.

