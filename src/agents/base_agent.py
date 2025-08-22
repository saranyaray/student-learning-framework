from crewai import Agent


class BaseStudentAgent:
    def __init__(self, role, goal, backstory, llm_model):
        self.agent = Agent(
            role=role, goal=goal, backstory=backstory, llm=llm_model, verbose=True
        )
