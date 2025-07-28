from agents import Agent, Runner
from config.sdk_client import model, config

resource_agent = Agent(
    name="ResourceAgent",
    instructions="""
You are an education advisor. Provide free learning resources and websites for a given career path.
Include popular platforms like Coursera, edX, freeCodeCamp, and relevant YouTube channels.
""",
    model=model
)

async def get_resources(field):
    prompt = f"Give free learning resources for {field}."
    result = await Runner.run(resource_agent, prompt, run_config=config)
    return result.final_output
