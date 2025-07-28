from agents import Agent, Runner
from config.sdk_client import model, config
from .CareerAgent import get_career_paths
from .SkillAgent import get_skill_roadmap
from .JobAgent import get_job_roles
from .ResourceAgent import get_resources
import re
from typing import Dict, Any, Tuple

class HandoffManager:
    """
    Manages handoffs between Career, Skill, and Job Agents based on user intent and conversation context.
    """
    
    def __init__(self):
        # Create a coordinator agent to determine which agent should handle the request
        self.coordinator_agent = Agent(
            name="CoordinatorAgent",
            instructions="""
You are a conversation coordinator for a career mentoring system. Analyze user messages and determine which agent should handle the request.

Available agents:
- CareerAgent: Suggests career paths based on interests
- SkillAgent: Creates skill roadmaps for specific careers
- JobAgent: Lists job roles in specific fields
- ResourceAgent: Provides learning resources

Respond with ONLY the agent name that should handle this request: CareerAgent, SkillAgent, JobAgent, or ResourceAgent.

Examples:
- "What career should I pursue in tech?" -> CareerAgent
- "I want to become a data scientist, what skills do I need?" -> SkillAgent
- "What jobs are available in marketing?" -> JobAgent
- "Where can I learn Python programming?" -> ResourceAgent
""",
            model=model
        )
        
        self.agent_functions = {
            'CareerAgent': get_career_paths,
            'SkillAgent': get_skill_roadmap,
            'JobAgent': get_job_roles,
            'ResourceAgent': get_resources
        }
        
        self.conversation_history = []
    
    async def determine_agent(self, user_input: str) -> str:
        """
        Determine which agent should handle the user's request.
        """
        prompt = f"User message: '{user_input}'"
        result = await Runner.run(self.coordinator_agent, prompt, run_config=config)
        
        # Extract agent name from response
        agent_name = result.final_output.strip()
        
        # Validate agent name
        if agent_name not in self.agent_functions:
            # Default to CareerAgent if unclear
            agent_name = 'CareerAgent'
        
        return agent_name
    
    async def handoff_to_agent(self, user_input: str, context: Dict[str, Any] = None) -> Tuple[str, str, str]:
        """
        Handoff the request to the appropriate agent and return the response.
        
        Returns:
            Tuple of (agent_name, response, next_suggested_agent)
        """
        # Determine which agent should handle this request
        selected_agent = await self.determine_agent(user_input)
        
        # Get the appropriate function
        agent_function = self.agent_functions[selected_agent]
        
        # Execute the agent function
        if selected_agent == 'CareerAgent':
            response = await agent_function(user_input)
            # After career suggestion, suggest skill roadmap
            next_agent = 'SkillAgent'
        elif selected_agent == 'SkillAgent':
            # Extract career from context or use user input
            career = context.get('career', user_input) if context else user_input
            response = await agent_function(career)
            # After skill roadmap, suggest job roles
            next_agent = 'JobAgent'
        elif selected_agent == 'JobAgent':
            # Extract field from context or use user input
            field = context.get('career', user_input) if context else user_input
            response = await agent_function(field)
            # After job roles, suggest resources
            next_agent = 'ResourceAgent'
        else:  # ResourceAgent
            # Extract field from context or use user input
            field = context.get('career', user_input) if context else user_input
            response = await agent_function(field)
            # After resources, cycle back to career for new queries
            next_agent = 'CareerAgent'
        
        # Update conversation history
        self.conversation_history.append({
            'user_input': user_input,
            'agent': selected_agent,
            'response': response,
            'context': context
        })
        
        return selected_agent, response, next_agent
    
    async def smart_handoff_flow(self, user_input: str) -> Dict[str, Any]:
        """
        Intelligent handoff flow that can chain multiple agents based on the request.
        """
        # Start with determining the primary agent
        primary_agent, primary_response, next_agent = await self.handoff_to_agent(user_input)
        
        result = {
            'primary_agent': primary_agent,
            'primary_response': primary_response,
            'handoff_chain': []
        }
        
        # If this is a career query, automatically chain to other relevant agents
        if primary_agent == 'CareerAgent' and primary_response:
            # Extract the first career suggestion for chaining
            career_lines = primary_response.strip().split('\n')
            first_career = career_lines[0].strip() if career_lines else user_input
            
            context = {'career': first_career}
            
            # Chain to SkillAgent
            skill_agent, skill_response, _ = await self.handoff_to_agent(
                first_career, context
            )
            result['handoff_chain'].append({
                'agent': skill_agent,
                'response': skill_response
            })
            
            # Chain to JobAgent
            job_agent, job_response, _ = await self.handoff_to_agent(
                first_career, context
            )
            result['handoff_chain'].append({
                'agent': job_agent,
                'response': job_response
            })
            
            # Chain to ResourceAgent
            resource_agent, resource_response, _ = await self.handoff_to_agent(
                first_career, context
            )
            result['handoff_chain'].append({
                'agent': resource_agent,
                'response': resource_response
            })
        
        return result
    
    def get_conversation_history(self) -> list:
        """
        Get the conversation history for context.
        """
        return self.conversation_history
    
    def clear_history(self):
        """
        Clear the conversation history.
        """
        self.conversation_history = []

# Convenience functions for easy integration
handoff_manager = HandoffManager()

async def process_with_handoff(user_input: str, use_smart_flow: bool = True) -> Dict[str, Any]:
    """
    Process user input with intelligent agent handoff.
    
    Args:
        user_input: The user's message
        use_smart_flow: Whether to use smart chaining of agents
    
    Returns:
        Dictionary containing agent responses and handoff information
    """
    if use_smart_flow:
        return await handoff_manager.smart_handoff_flow(user_input)
    else:
        agent, response, next_agent = await handoff_manager.handoff_to_agent(user_input)
        return {
            'primary_agent': agent,
            'primary_response': response,
            'next_suggested_agent': next_agent,
            'handoff_chain': []
        }

async def manual_handoff(user_input: str, target_agent: str, context: Dict[str, Any] = None) -> str:
    """
    Manually handoff to a specific agent.
    
    Args:
        user_input: The user's message
        target_agent: The target agent name (CareerAgent, SkillAgent, JobAgent, ResourceAgent)
        context: Optional context dictionary
    
    Returns:
        The agent's response
    """
    if target_agent not in handoff_manager.agent_functions:
        raise ValueError(f"Invalid agent: {target_agent}")
    
    agent_function = handoff_manager.agent_functions[target_agent]
    
    if context and 'career' in context:
        return await agent_function(context['career'])
    else:
        return await agent_function(user_input)
