from agents import Agent, Runner
from config.sdk_client import model, config

skill_agent = Agent(
    name="SkillAgent",
    instructions="""
You are a career mentor. Create a detailed skill roadmap for a given career field.
Provide a step-by-step learning path with key skills, tools, and milestones.
""",
    model=model
)

async def get_skill_roadmap(field):
    prompt = f"Show skill roadmap for {field}."
    result = await Runner.run(skill_agent, prompt, run_config=config)
    return result.final_output
