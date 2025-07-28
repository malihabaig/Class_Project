from agents import Agent, Runner
from config.sdk_client import model, config

job_agent = Agent(
    name="JobAgent",
    instructions="""
You are a job market guide. List 3–4 real-world jobs related to a field in bullet points.
""",
    model=model
)

async def get_job_roles(field):
    prompt = f"List job roles in {field}."
    result = await Runner.run(job_agent, prompt, run_config=config)
    return result.final_output
