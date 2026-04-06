# Recruitment-Agency-Workflow
I built an AI-based candidate screening system using LangGraph and an LLM. LangGraph helped me design a stateful workflow with multiple steps and conditional routing, instead of simple if-else logic.

I used an LLM to analyze unstructured resume text, replacing rule-based logic with intelligent decision-making. Through prompt engineering, I ensured consistent outputs like “Match” or “No Match.”

I maintained data across steps using a state object, and structured the system into modular nodes like experience classification and skill evaluation. Based on results, conditional edges decide whether to shortlist, reject, or escalate the candidate.

Finally, I used Streamlit for the UI and .env for secure API key management, making the system interactive and deployment-ready.

