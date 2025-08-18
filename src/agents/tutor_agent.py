from .base_agent import BaseStudentAgent
from config.settings import OLLAMA_AGENTS

class TutorAgent(BaseStudentAgent):
    def __init__(self):
        super().__init__(
            role="Tutor: Phi3",
            goal="Explain concepts with clarity and foundational knowledge using provided context.",
            backstory="A patient tutor who focuses on basics and clear examples.",
            llm_model=OLLAMA_AGENTS['tutor']
        )
