# CareerMate – Multi-Agent Career Advisor

This repository showcases how to build a multi-agent career advisor system using the OpenAI Agents SDK. CareerMate helps users explore career paths, identify skill gaps, discover job opportunities, and find relevant online courses — all through natural language chat.

## Project Structure

- `CareerMate.py` – Core implementation of the career agents (SkillGap, JobMatch, CourseRecommender)
- `streamlit_UI_View` – Streamlit UI with a sidebar to select job title, enter skills, and display results in chat

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file:

```
BASE_URL="https://models.github.ai/inference/v1"
API_KEY=
MODEL_NAME="openai/gpt-4.1-nano"
```

## Running the CareerMate App

### Streamlit Web Interface

Launch the full CareerMate UI:

```bash
streamlit run .\streamlit_UI_View.py
```

Features include:
- Sidebar with job selection and skill input
- Personalized recommendations for jobs, courses, and skill gaps
- Plaintext, readable chat format with timestamps
- Background-styled UI and chat bubbles

### Command Line Examples

To test the agents via terminal:

```bash
python .\CareerMate.py
```

This will run sample queries through the full career assistant agent.

## Features Demonstrated

1. **Multi-Agent System**
   - Intent-aware conversation controller
   - Handoff to Skill Gap, Job Finder, and Course Recommender agents

2. **Structured Tools**
   - Custom tools for comparing skills, searching dummy jobs, and recommending learning resources

3. **Streamlit Frontend**
   - Conversational UI
   - Interactive input for job goals and current skillset
   - Styled output per agent response

4. **Dummy Data Simulation**
   - Jobs, skills, and course data for demonstration
   - Real APIs can be integrated in production

## Notes

This is a prototype for career planning and uses simulated data. You can easily plug in real APIs (e.g., LinkedIn Jobs, Coursera, EdX) for production use.

Built with ❤️ using the OpenAI Agents SDK and Streamlit.
