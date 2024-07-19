from langchain_community.llms import Ollama
# from langchain_community.agent_toolkits.load_tools import load_tools
from crewai import Agent, Crew, Task, Process

model = Ollama(model="llama3")
# tools = load_tools(["human", "llm-math"], llm=model)
verbose = True

query = "Help me with a workout plan."

# Agents
class FitnessAgents():
    def lead_coach(self):
        return Agent(
            role="Lead Coach",
            goal=f"Understand the users needs: {query}, and tailor specialized query to pass to 'Fitness Trainer' and 'Nutrionist' and use their response to compile a well detailed fitness routine for the user.",
            backstory="With extensive experience in managing fitness programs and a strong background in exercise science and health coaching, you have successfully guided numerous clients through comprehensive fitness journeys. Your expertise in tailoring plans and strategic oversight helps clients achieve significant results.",
            verbose=verbose,
            allow_delegation=True,
            llm=model,
            max_iter=20,
        )


    def fitness_trainer(self):
        return Agent(
            role="Fitness Trainer",
            goal="Make a custom, well-detailed training plan according to users need to help him achieve his goals.",
            backstory="With a background in personal training and certification in strength and conditioning, you have a proven track record of helping clients build muscle, loose weight and improve their fitness levels. Your passion for fitness and dedication to personalized workout plans and support make you an invaluable part of the team.",
            # tools=tools,
            verbose=verbose,
            allow_delegation=False,
            llm=model,
        )

    def nutritionist(self):
        return Agent(
            role="Nutritionist",
            goal="Make a custom diet plan which complement user's fitness regimen, promotes muscle growth, and supports overall health while fitting within their constraints (such as hostel living or limited available materials). You aim to provide practical and sustainable dietary recommendations.",
            backstory="With a degree in nutrition or dietetics and certification in your field, you have experience working with athletes and individuals with specific dietary needs. Your expertise includes meal planning, nutrient timing, and understanding the relationship between diet and exercise performance.",
            # tools=tools,
            verbose=verbose,
            allow_delegation=False,
            llm=model,
        )

# Tasks
class FitnessTasks:
    def manage_fitness_goals(self, agent):
        return Task(
            description=f"Understand the user's needs from the given query: `{query}`. Based on this, provide a structured output specifying the tasks for 'Fitness Trainer' and 'Nutritionist'. The output should include detailed questions to ask the user if necessary, and instructions for each agent.",
            agent=agent,
            expected_output="JSON format with fields 'fitness_tasks' and 'nutrition_tasks'. Example: {'fitness_tasks': 'Design strength training routine', 'nutrition_tasks': 'Create a muscle gain diet plan', 'questions': ['What is the user's current fitness level?']}."
        )

    def generate_fitness_routine(self, agent, context):
        return Task(
            description="Use the 'fitness_tasks' field from the output of 'manage_fitness_tasks' to generate a relevant and structured fitness routine. If needed, ask user to provide further details or clarifications based on user requirements.",
            agent=agent,
            context=context,
            expected_output="A detailed and structured fitness routine based on the input query."
        )

    def generate_diet_plan(self, agent, context):
        return Task(
            description="Use the 'nutrition_tasks' field from the output of 'manage_fitness_tasks' to create a relevant and structured diet plan. If needed, ask user to provide further details or clarifications based on user requirements.",
            agent=agent,
            context=context,
            expected_output="A comprehensive and structured diet plan based on the input query."
        )

# Initialize the Crew with the agents and tasks
agents = FitnessAgents()
tasks = FitnessTasks()

coach = agents.lead_coach()
trainer = agents.fitness_trainer()
nutritionist = agents.nutritionist()

manage_fitness_goals = tasks.manage_fitness_goals(coach)
generate_fitness_routine = tasks.generate_fitness_routine(trainer, [manage_fitness_goals])
generate_diet_plan = tasks.generate_diet_plan(nutritionist, [manage_fitness_goals]) # can add fitness routine also to tailor diet according to that


crew = Crew(
    agents=[coach, trainer, nutritionist],
    tasks=[manage_fitness_goals, generate_fitness_routine, generate_diet_plan],
    process=Process.hierarchical,
    manager_llm=model,
    verbose=verbose,
)

# Execute the Crew process and handle the output
output = crew.kickoff()
print(output)