from config.settings import OLLAMA_AGENTS

from .base_agent import BaseStudentAgent


class SynthesizerAgent(BaseStudentAgent):
    def __init__(self):
        super().__init__(
            role="Synthesizer",
            goal=(
                "Read the three expert answers. Extract unique points from each. "
                "Create a short, numbered list (3-5 points max) with no repetition. "
                "Keep each point to 1-2 sentences only."
            ),
            backstory=(
                "You are a concise editor who hates repetition. Your job is to take "
                "expert answers and turn them into a brief, numbered summary that "
                "students can read quickly without seeing the same point twice."
            ),
            llm_model=OLLAMA_AGENTS["synthesizer"],
        )
