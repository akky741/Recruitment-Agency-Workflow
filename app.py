import os
import streamlit as st
from dotenv import load_dotenv

#pip install langchain langchain-core langchain-community langgraph langchain-openai python-dotenv

# Load env variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# LLM
from langchain_openai.chat_models import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")

# State
from typing_extensions import TypedDict

class State(TypedDict):
    application: str
    experience_level: str
    skill_match: str
    response: str

# LangGraph
from langgraph.graph import StateGraph, START, END
workflow = StateGraph(State)

from langchain_core.prompts import ChatPromptTemplate

# ---------------- NODES ---------------- #

def categorize_experience(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "Based on the following job application, categorize the candidate as "
        "'Entry-level', 'Mid-level', or 'Senior-level'.\n"
        "Application: {application}"
    )
    chain = prompt | llm
    result = chain.invoke({"application": state["application"]}).content.strip()
    return {"experience_level": result}


def assess_skillset(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "Based on the job application for a Python Developer, assess the candidate's skillset.\n"
        "Respond ONLY with 'Match' or 'No Match'.\n"
        "Application: {application}"
    )
    chain = prompt | llm
    result = chain.invoke({"application": state["application"]}).content.strip()
    return {"skill_match": result}


def schedule_hr_interview(state: State) -> State:
    return {"response": "✅ Candidate shortlisted for HR interview"}


def escalate_to_recruiter(state: State) -> State:
    return {"response": "⚠️ Escalated to recruiter (Senior but skill mismatch)"}


def reject_application(state: State) -> State:
    return {"response": "❌ Candidate rejected (Not matching JD)"}


# ---------------- ROUTING ---------------- #

def route_app(state: State) -> str:
    if "Match" in state["skill_match"]:
        return "schedule_hr_interview"
    elif "Senior" in state["experience_level"]:
        return "escalate_to_recruiter"
    else:
        return "reject_application"


# ---------------- GRAPH ---------------- #

workflow.add_node("categorize_experience", categorize_experience)
workflow.add_node("assess_skillset", assess_skillset)
workflow.add_node("schedule_hr_interview", schedule_hr_interview)
workflow.add_node("escalate_to_recruiter", escalate_to_recruiter)
workflow.add_node("reject_application", reject_application)

workflow.add_edge(START, "categorize_experience")
workflow.add_edge("categorize_experience", "assess_skillset")
workflow.add_conditional_edges("assess_skillset", route_app)

workflow.add_edge("schedule_hr_interview", END)
workflow.add_edge("escalate_to_recruiter", END)
workflow.add_edge("reject_application", END)

app_graph = workflow.compile()

# ---------------- FUNCTION ---------------- #

def run_screening(application):
    result = app_graph.invoke({"application": application})
    return result


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="AI Candidate Screening", layout="centered")

st.title("🤖 AI Candidate Screening System")
st.markdown("Automated Resume Screening using LangGraph + LLM")

application_text = st.text_area(
    "Enter Candidate Application:",
    placeholder="Example: I have 3 years of experience in Python, ML, and SQL..."
)

if st.button("Evaluate Candidate"):

    if application_text.strip() == "":
        st.warning("Please enter application text")
    else:
        with st.spinner("Analyzing..."):
            result = run_screening(application_text)

        st.subheader("📊 Results")

        st.write(f"**Experience Level:** {result.get('experience_level')}")
        st.write(f"**Skill Match:** {result.get('skill_match')}")
        st.write(f"**Final Decision:** {result.get('response')}")

        # Visual indicator
        if "shortlisted" in result.get("response", "").lower():
            st.success("Candidate Selected ✅")
        elif "rejected" in result.get("response", "").lower():
            st.error("Candidate Rejected ❌")
        else:
            st.warning("Needs Recruiter Review ⚠️")