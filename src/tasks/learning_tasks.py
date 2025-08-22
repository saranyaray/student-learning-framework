from crewai import Task


def build_expert_task(agent, description, context, question):
    return Task(
        description=(
            f"{description}\n\n"
            "You are an expert tutor. Use the provided context to answer the "
            "student's question.\n"
            "1. Restate the question briefly to confirm understanding.\n"
            "2. Provide a clear, step-by-step explanation that connects directly "
            "to the context.\n"
            "3. Use simple language and add examples if helpful.\n"
            "4. If the context does not fully cover the answer, acknowledge the "
            "gap and give the best possible explanation.\n\n"
            f"Context from documents:\n{context}\n\n"
            f"Student Question: {question}"
        ),
        agent=agent.agent,
        expected_output=(
            "A clear, structured explanation in 2–4 short paragraphs. "
            "Include examples or analogies where relevant."
        ),
    )


def build_synthesis_task(agent, expert_answers):
    return Task(
        description=(
            "You are a synthesis expert. Read the expert answers below carefully. "
            "1. Identify the unique insights or perspectives in each answer.\n"
            "2. Remove any duplication or overlapping points.\n"
            "3. Produce a concise, numbered list (3–5 items).\n"
            "4. Each item must be 1–2 sentences, clear, and directly based on "
            "the answers.\n\n"
            f"Expert answers:\n{expert_answers}"
        ),
        agent=agent.agent,
        expected_output=(
            "A numbered list of 3–5 unique insights, each written as 1–2 sentences. "
            "No repetition, no extra commentary."
        ),
    )
