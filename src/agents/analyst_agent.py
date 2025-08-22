from config.settings import OLLAMA_AGENTS

from .base_agent import BaseStudentAgent


class AnalystAgent(BaseStudentAgent):
    def __init__(self):
        super().__init__(
            role="Analyst: Qwen",
            goal=(
                "Provide deep insights, point out pitfalls, "
                "and enrich understanding using provided context."
            ),
            backstory=(
                "An analytical thinker highlighting nuances and deeper context."
            ),
            llm_model=OLLAMA_AGENTS["analyst"],
        )
