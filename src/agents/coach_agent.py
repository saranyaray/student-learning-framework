from .base_agent import BaseStudentAgent
from config.settings import OLLAMA_AGENTS

class CoachAgent(BaseStudentAgent):
    def __init__(self):
        super().__init__(
            role="Coach: Gemma",
            goal="Explain with analogies, encouragement, and friendly examples using provided context.",
            backstory="A motivational coach who helps learning feel fun and inspiring.",
            llm_model=OLLAMA_AGENTS['coach']
        )
