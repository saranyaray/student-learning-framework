from config.settings import OLLAMA_AGENTS

from .base_agent import BaseStudentAgent


class SynthesizerAgent(BaseStudentAgent):
    def __init__(self):
        super().__init__(
            role="Synthesizer",
            goal=(
                "Carefully examine and compare multiple pieces of input from "
                "different sources. Distill the most important, non-redundant "
                "points, and present a concise synthesis for the user."
            ),
            backstory=(
                "You specialize in combining information from multiple perspectives, "
                "eliminating overlap and providing clear, user-friendly summaries."
            ),
            llm_model=OLLAMA_AGENTS["synthesizer"],
        )
