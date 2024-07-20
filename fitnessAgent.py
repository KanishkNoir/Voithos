from langchain_community.llms import Ollama
from langchain_community.agent_toolkits.load_tools import load_tools
from crewai import Agent, Crew, Task, Process
from tools.search_tools import SearchTools
from dotenv import load_dotenv

model = Ollama(model="llama3")
load_dotenv()
verbose = True

# User Query
query = "Help me with a workout plan."

# Agents
class FitnessAgents():
    def fitness_trainer(self):
        return Agent(
            role="Fitness Trainer",
            goal="Make a custom, well-detailed training plan according to user's needs to help achieve desired goals. You can search the internet to find relevant data and content to generate your answer, but use it only once to gather information, after that reflect on the data and write a plan accordinly.",
            backstory="With a background in personal training and certification in strength and conditioning, you have a proven track record of helping clients build muscle, loose weight and improve their fitness levels. Your passion for fitness and dedication to personalized workout plans and support make you an invaluable part of the team.",
            tools=[SearchTools.search_internet],
            verbose=verbose,
            allow_delegation=False,
            llm=model,
            max_iter=10
        )

    def nutritionist(self):
        return Agent(
            role="Nutritionist",
            goal="Make a custom diet plan which complement user's fitness regimen, and required needs. You aim to provide practical and sustainable dietary recommendations. You can also search the internet to find relevant data and content to generate your answer, but  use it only once to gather information, after that reflect on the data and writer write accordinly.",
            backstory="With a degree in nutrition or dietetics and certification in your field, you have experience working with athletes and individuals with specific dietary needs. Your expertise includes meal planning, nutrient timing, and understanding the relationship between diet and exercise performance.",
            tools=[SearchTools.search_internet],
            verbose=verbose,
            allow_delegation=False,
            llm=model,
            max_iter=10
        )
        
    def plan_writer(self):
        return Agent(
            role="Plan Writer",
            goal="Writing detailed customized fintess and nutrion plans for clients incorporating the details received from other agents.",
            backstory="With extensive experience in managing fitness programs and a strong background in exercise science and health coaching, you have successfully guided numerous clients through comprehensive fitness journeys. Your expertise in tailoring plans and strategic oversight helps clients achieve significant results.",
            verbose=verbose,
            allow_delegation=True,
            llm=model,
        )

# Tasks
class FitnessTasks:
    def generate_fitness_routine(self, agent):
        return Task(
            description=f"Create a Personalized Workout Plan for client, based on the query: {query} and searched results from the internet(if any).",
            agent=agent,
            expected_output="A detailed and structured fitness routine based on the input query."
        )

    def generate_diet_plan(self, agent, context):
        return Task(
            description=f"Design a Customized Meal Plan for client, based on the training_regime:{context} and intial_query:{query}.",
            agent=agent,
            context=context,
            expected_output="A comprehensive and structured diet plan based on the input query."
        )

    def write_plans(self, agent, context):
        return Task(
            description=f"With the help of the content provided by 'fitness_trainer' and 'nutritionist' agents: {context}, Write a Detailed Fitness and Nutrition Plan for the week.",
            agent=agent,
            context=context,
            expected_output="Well formated and structured weekly fitness and diet plan according to the user's needs."
        )

# Initialize the Crew with the agents and tasks
agents = FitnessAgents()
tasks = FitnessTasks()

trainer = agents.fitness_trainer()
nutritionist = agents.nutritionist()
writer = agents.plan_writer()

generate_fitness_routine = tasks.generate_fitness_routine(trainer)
generate_diet_plan = tasks.generate_diet_plan(nutritionist, [generate_fitness_routine])
write_plan = tasks.write_plans(writer, [generate_fitness_routine, generate_diet_plan])

crew = Crew(
    agents=[trainer, nutritionist, writer],
    tasks=[generate_fitness_routine, generate_diet_plan, write_plan],
    process=Process.sequential,
    verbose=verbose,
)

# Execute the Crew process and handle the output
output = crew.kickoff()
print(output)