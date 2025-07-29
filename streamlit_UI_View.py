import streamlit as st
import asyncio
import uuid
from datetime import datetime
from typing import List
from agents import Runner
from CareerMate import conversation_agent, SkillGapAnalysis, JobMatch, CourseSuggestion

# Streamlit app configuration
st.set_page_config(
    page_title="CareerMate Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.chat-box {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.user-label {
    font-weight: bold;
    color: #2196F3;
}
.assistant-label {
    font-weight: bold;
    color: #4CAF50;
}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Sidebar options
with st.sidebar:
    st.title("CareerMate Options")
    mode = st.selectbox("Choose advisor mode:", ["Skill Gap Analysis", "Job Finder", "Course Recommender", "Auto Detect"], index=3)
    selected_job = st.selectbox("Select a Target Job", ["Data Scientist", "Web Developer", "Data Analyst"])
    skills_input = st.text_area("Your Current Skills (comma-separated)", "Python, Excel")
    st.markdown("""---""")
    if st.button("Submit Skills & Job"):
        prefill_query = f"I want to become a {selected_job.lower()} and I know {skills_input.strip()}"
        timestamp = datetime.now().strftime("%I:%M %p")
        st.session_state.chat_history.append({"role": "user", "content": prefill_query, "timestamp": timestamp})
        st.session_state.processing_message = prefill_query
        st.rerun()

    if st.button("Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.success("New conversation started!")

# Format agent response
def format_response(output):
    if hasattr(output, "model_dump"):
        output = output.model_dump()

    if isinstance(output, dict):
        if "missing_skills" in output:
            return f"""
🧠 Skill Gap Analysis\nMissing Skills: {', '.join(output['missing_skills'])}\nReason: {output['reason']}"""
        elif "company" in output:
            return f"""
💼 Job Match\nTitle: {output['title']}\nCompany: {output['company']}\nLocation: {output['location']}\nWhy this job: {output['match_reason']}"""
        elif "platform" in output:
            return f"""
📖 Course Recommendation\nSkill: {output['skill']}\nCourse: {output['title']}\nPlatform: {output['platform']}\nLink: {output['link']}"""
    return str(output)

# Input handler
def handle_input(user_input: str):
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({"role": "user", "content": user_input, "timestamp": timestamp})
    st.session_state.processing_message = user_input

# Chat UI
st.title(":brain: CareerMate Advisor")
st.caption("Explore careers, find jobs, fill skill gaps, and upskill – all in one chat!")

# Display messages
for msg in st.session_state.chat_history:
    role_label = "You" if msg["role"] == "user" else "CareerMate"
    label_class = "user-label" if msg["role"] == "user" else "assistant-label"
    st.markdown(f"""
<div class='chat-box'>
    <div class='{label_class}'>{role_label} ({msg['timestamp']}):</div>
    <div>{msg['content']}</div>
</div>
""", unsafe_allow_html=True)

# Input box
user_text = st.chat_input("Ask about jobs, skills, or courses...")
if user_text:
    handle_input(user_text)
    st.rerun()

# Process new message
if st.session_state.processing_message:
    with st.spinner("Thinking..."):
        try:
            input_list = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.chat_history
                if msg["role"] in ["user", "assistant"]
            ]

            result = asyncio.run(Runner.run(conversation_agent, input_list))
            response_text = format_response(result.final_output).strip()

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        st.session_state.processing_message = None
        st.rerun()

# Footer
st.divider()
st.caption("Built with 🚀 by JNR Team")
