from agents import Agent, Runner
from config.sdk_client import model, config

career_agent = Agent(
    name="CareerAgent",
    instructions="""
You are a career expert. Suggest 2–3 professional career paths based on a user's interest.
Only give one per line.
""",
    model=model
)

async def get_career_paths(interest):
    prompt = f"Suggest career paths for someone interested in {interest}."
    result = await Runner.run(career_agent, prompt, run_config=config)
    return result.final_output
