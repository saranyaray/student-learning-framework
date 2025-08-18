from crewai import Task

def build_expert_task(agent, description, context, question):
    return Task(
        description=f"{description}\n\nContext from documents:\n{context}\n\nStudent Question: {question}",
        agent=agent.agent,
        expected_output="A helpful explanation based on the provided context and question."
    )

def build_synthesis_task(agent, expert_answers):
    return Task(
        description=f"Combine these three expert answers into a single answer:\n\n{expert_answers}",
        agent=agent.agent,
        expected_output="A polished, engaging answer perfect for students—combines clarity, examples, and depth."
    )
