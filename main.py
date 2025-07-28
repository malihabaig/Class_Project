import streamlit as st
import asyncio
from multi.HandoffManager import process_with_handoff, manual_handoff, handoff_manager
from multi.CareerAgent import get_career_paths
from multi.SkillAgent import get_skill_roadmap
from multi.JobAgent import get_job_roles
from multi.ResourceAgent import get_resources

st.set_page_config(page_title="💼 Career Mentor Pro", layout="wide")
st.title("💼 Career Mentor Agent Pro")
st.subheader("Get personalized career guidance with AI-powered agent handoffs")

# Sidebar for mode selection
st.sidebar.title("🔄 Agent Handoff Options")
mode = st.sidebar.radio(
    "Choose interaction mode:",
    ["🤖 Smart Handoff (Automatic)", "🎯 Manual Agent Selection", "📊 Classic Flow"]
)

user_input = st.text_input("What's your passion, interest, or career question?")

if mode == "🤖 Smart Handoff (Automatic)":
    st.sidebar.markdown("""
    **Smart Handoff Mode:**
    - AI automatically determines the best agent
    - Chains multiple agents when appropriate
    - Provides comprehensive career guidance
    """)
    
    if st.button("🚀 Get Smart Career Guidance") and user_input:
        with st.spinner("🤖 AI is determining the best approach..."):
            result = asyncio.run(process_with_handoff(user_input, use_smart_flow=True))
            
            # Display primary response
            st.success(f"🎯 **{result['primary_agent']}** handled your request:")
            st.markdown(result['primary_response'])
            
            # Display handoff chain if available
            if result['handoff_chain']:
                st.markdown("---")
                st.markdown("### 🔄 **Agent Handoff Chain:**")
                
                agent_icons = {
                    'SkillAgent': '🛠',
                    'JobAgent': '💼',
                    'ResourceAgent': '📚',
                    'CareerAgent': '🌟'
                }
                
                for handoff in result['handoff_chain']:
                    agent_name = handoff['agent']
                    icon = agent_icons.get(agent_name, '🤖')
                    st.markdown(f"#### {icon} **{agent_name}**")
                    st.markdown(handoff['response'])
                    st.markdown("")

elif mode == "🎯 Manual Agent Selection":
    st.sidebar.markdown("""
    **Manual Selection Mode:**
    - Choose specific agent for your query
    - Direct control over which agent responds
    - Perfect for targeted questions
    """)
    
    selected_agent = st.sidebar.selectbox(
        "Select Agent:",
        ["CareerAgent", "SkillAgent", "JobAgent", "ResourceAgent"],
        help="Choose which agent should handle your request"
    )
    
    agent_descriptions = {
        "CareerAgent": "🌟 Suggests career paths based on interests",
        "SkillAgent": "🛠 Creates detailed skill roadmaps",
        "JobAgent": "💼 Lists relevant job roles and positions",
        "ResourceAgent": "📚 Provides learning resources and materials"
    }
    
    st.sidebar.info(agent_descriptions[selected_agent])
    
    if st.button(f"🎯 Ask {selected_agent}") and user_input:
        with st.spinner(f"🤖 {selected_agent} is processing your request..."):
            response = asyncio.run(manual_handoff(user_input, selected_agent))
            
            agent_icons = {
                'CareerAgent': '🌟',
                'SkillAgent': '🛠',
                'JobAgent': '💼',
                'ResourceAgent': '📚'
            }
            
            icon = agent_icons.get(selected_agent, '🤖')
            st.success(f"{icon} **{selected_agent}** Response:")
            st.markdown(response)
            
            # Show handoff suggestions
            st.markdown("---")
            st.markdown("### 🔄 **Suggested Next Steps:**")
            
            next_agents = {
                'CareerAgent': ['SkillAgent', 'JobAgent'],
                'SkillAgent': ['JobAgent', 'ResourceAgent'],
                'JobAgent': ['ResourceAgent', 'SkillAgent'],
                'ResourceAgent': ['CareerAgent', 'SkillAgent']
            }
            
            cols = st.columns(len(next_agents.get(selected_agent, [])))
            for i, next_agent in enumerate(next_agents.get(selected_agent, [])):
                with cols[i]:
                    if st.button(f"➡️ Ask {next_agent}", key=f"next_{next_agent}"):
                        st.rerun()

else:  # Classic Flow
    st.sidebar.markdown("""
    **Classic Flow Mode:**
    - Original parallel processing
    - All agents run simultaneously
    - Complete career overview
    """)
    
    if st.button("📊 Explore Career Path (Classic)") and user_input:
        with st.spinner("🔍 Finding best career options for you..."):

            async def run_agents_flow():
                careers = await get_career_paths(user_input)
                career = careers.split("\n")[0].strip()

                # Run the other 3 agents in parallel
                skill_task = asyncio.create_task(get_skill_roadmap(career))
                job_task = asyncio.create_task(get_job_roles(career))
                resource_task = asyncio.create_task(get_resources(career))

                skill = await skill_task
                jobs = await job_task
                resources = await resource_task

                return career, skill, jobs, resources

            career, skill, jobs, resources = asyncio.run(run_agents_flow())

            st.success(f"🌟 Suggested Career Path: {career}")
            st.markdown(f"### 🛠 Skill Roadmap\n{skill}")
            st.markdown(f"### 💼 Job Roles\n{jobs}")
            st.markdown(f"### 📚 Learning Resources\n{resources}")

# Conversation History Section
if st.sidebar.button("📜 Show Conversation History"):
    history = handoff_manager.get_conversation_history()
    if history:
        st.sidebar.markdown("### 📜 **Recent Interactions:**")
        for i, interaction in enumerate(history[-3:]):  # Show last 3 interactions
            st.sidebar.markdown(f"**{i+1}.** {interaction['agent']}: {interaction['user_input'][:50]}...")
    else:
        st.sidebar.info("No conversation history yet.")

if st.sidebar.button("🗑️ Clear History"):
    handoff_manager.clear_history()
    st.sidebar.success("History cleared!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 Powered by AI Agent Handoffs | Choose your preferred interaction mode above</p>
</div>
""", unsafe_allow_html=True)
