from crewai import Agent, Crew, LLM, Task


# Generate an RTI asking for reasons and work done on the issue.
def generate_rti(context):
    context = context.strip()
    available_characters = 700 - len(context) - 1

    model = LLM(
        model="ollama/qwen3:0.6b",
        base_url="http://localhost:11434",
        temperature=0.1,
        max_tokens=700,
        timeout=90,
        extra_body={"think": False},
    )

    agent = Agent(
        role="RTI Writer",
        goal="Write formal RTI applications requesting official records.",
        backstory="You write clear RTI queries using only the supplied facts.",
        llm=model,
        max_iter=2,
    )

    prompt = f"""
        Draft the body of a formal RTI application based on this context:
        {context}

        Begin with: "Kindly provide certified copies of the following records:"
        Use clear numbered points requesting:
        1. Recorded reasons and relevant file notes concerning the issue described in the context.
        2. Relevant inspection findings and action-taken reports on completed and ongoing corrective work, including dates and present status.
        3. Funds sanctioned, released and spent on these works, with supporting records.
        4. Pending work, approved completion timelines and the offices assigned responsibility, as recorded.

        Use polite, neutral and precise language. Ask for information held in records,
        not personal opinions or a newly prepared explanation. Keep the supplied values,
        units, location and time period accurate. Do not assume a target or infer causes.
        Do not suggest possible causes,
        make allegations, invent facts, cite legal sections or add unrelated requests.

        The context is already included above the output, so do not repeat it.
        Aim for a complete application of 600-700 characters including that context.
        Your response alone must not exceed {available_characters} characters.
        Return only the application body. No greeting, signature, markdown, drafting
        instructions, character count or explanatory commentary. /no_think
        """

    task = Task(
        description=prompt,
        expected_output="A formal RTI requesting recorded reasons and action-taken reports.",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], tracing=False)
    result = crew.kickoff()
    query = result.raw.strip()
    text = context + " " + query

    if not query or len(text) > 700:
        raise ValueError("Could not generate an RTI within 700 characters. Try again.")

    return text
