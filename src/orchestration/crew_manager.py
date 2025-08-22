from crewai import Crew

from src.agents.analyst_agent import AnalystAgent
from src.agents.coach_agent import CoachAgent
from src.agents.synthesizer_agent import SynthesizerAgent
from src.agents.tutor_agent import TutorAgent
from src.tasks.learning_tasks import build_expert_task, build_synthesis_task


class StudentLearningCrew:
    def __init__(self, retriever):
        self.retriever = retriever

        # Initialize agents
        print("🤖 Initializing agents...")
        try:
            self.tutor = TutorAgent()
            self.coach = CoachAgent()
            self.analyst = AnalystAgent()
            self.synthesizer = SynthesizerAgent()

            # Verify all agents are created properly
            agents = [self.tutor, self.coach, self.analyst, self.synthesizer]
            for i, agent in enumerate(agents):
                if agent is None or agent.agent is None:
                    raise ValueError(f"Agent {i} failed to initialize properly")

            print("✅ All agents initialized successfully")

        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            raise

    def process_question(self, question):
        # FIXED: Use distance_threshold instead of similarity_threshold
        context = self.retriever.get_context(question, top_k=4)

        # Create tasks
        task1 = build_expert_task(
            self.tutor, "Provide a clear, foundational explanation", context, question
        )
        task2 = build_expert_task(
            self.coach, "Explain with analogies and encouragement", context, question
        )
        task3 = build_expert_task(
            self.analyst, "Provide deeper insights and analysis", context, question
        )

        expert_tasks = [task1, task2, task3]
        expert_outputs = {}

        # Run sequentially to avoid memory issues
        for i, task in enumerate(expert_tasks, 1):
            print(f"🤖 Running Expert {i}/3...")
            role, answer = self._run_task(task)
            expert_outputs[role] = answer
            print(f"✅ {role} completed")

        # Synthesis
        combined = "\n\n".join(expert_outputs.values())
        synth_task = build_synthesis_task(self.synthesizer, combined)
        synth_crew = Crew(
            agents=[self.synthesizer.agent], tasks=[synth_task], verbose=False
        )
        final_answer = synth_crew.kickoff()

        return {
            "context": context,
            "expert_outputs": expert_outputs,
            "final_answer": str(final_answer),
        }

    @staticmethod
    def _run_task(task):
        temp_crew = Crew(agents=[task.agent], tasks=[task], verbose=False)
        result = temp_crew.kickoff()
        return (task.agent.role, str(result))
