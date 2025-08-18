from .base_agent import BaseStudentAgent
from config.settings import OLLAMA_AGENTS

class SynthesizerAgent(BaseStudentAgent):
    def __init__(self):
        super().__init__(
            role="Synthesizer",
            goal="Synthesize, not just merge: read the expert answers, extract the most insightful or unique points from each (even if they disagree), and compose a new, improved answer for students that integrates and builds on the best parts.",
            backstory="A critical analyst and editor, skilled at reading expert solutions, identifying valuable points, resolving differences, and writing a synthesized, clear answer that goes beyond simple merging.",
            llm_model=OLLAMA_AGENTS['synthesizer']
        )
