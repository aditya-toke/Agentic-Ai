import streamlit as st
import json
import random
from datetime import datetime
import pandas as pd

from agent.state import AgentState
from agent.observer import observe
from agent.reasoner import reason
from agent.decider import decide
from agent.actor import act
from agent.memory import remember

st.set_page_config(page_title="Agentic AI Support", layout="wide")
st.title("🧠 Agentic AI – Self-Healing Support System")

st.experimental_autorefresh(interval=5000)

# ---------- Load company state ----------
with open("data/company_state.json") as f:
    company_state = json.load(f)

# ---------- Generate tickets dynamically ----------
def generate_tickets(state):
    tickets = []

    def ticket(merchant, issue, error):
        return {
            "ticket_id": f"T{random.randint(1000,9999)}",
            "merchant_id": merchant,
            "issue": issue,
            "error": error,
            "time": datetime.now().strftime("%H:%M:%S")
        }

    for m in state["webhook_missing"]:
        tickets.append(ticket(m, "Checkout page blank", "Missing webhook"))

    for m in state["api_key_invalid"]:
        tickets.append(ticket(m, "Payments failing", "401 API Unauthorized"))

    for m in state["frontend_not_deployed"]:
        tickets.append(ticket(m, "Home page not loading", "Frontend build not deployed"))

    for m in state["env_vars_missing"]:
        tickets.append(ticket(m, "Config error", "Missing environment variables"))

    return tickets

tickets = generate_tickets(company_state)
tickets_df = pd.DataFrame(tickets)

# ---------- Run agent ----------
agent_state = AgentState()
observe(agent_state, tickets)
reason(agent_state)
decide(agent_state)

# ---------- Dashboard ----------
st.subheader("📩 Recent Tickets")
st.dataframe(tickets_df, use_container_width=True)

st.subheader("📊 Pattern Detection")
pattern_df = tickets_df["error"].value_counts().reset_index()
pattern_df.columns = ["Error Type", "Ticket Count"]
st.bar_chart(pattern_df.set_index("Error Type"))

st.subheader("🧠 Agent Reasoning")
for h in agent_state.hypotheses:
    with st.expander(h["cause"]):
        st.write(f"Confidence: {h['confidence']}")
        st.write(f"Risk: {h['risk']}")
        st.write(f"Blast Radius: {h['blast_radius']}")

st.subheader("✅ Proposed Resolution")

if agent_state.decision["status"] == "blocked":
    st.error(agent_state.decision["reason"])
else:
    st.success(agent_state.decision["root_cause"])
    st.write(f"Confidence: {agent_state.decision['confidence']}")
    st.write(f"Risk: {agent_state.decision['risk']}")

    col1, col2 = st.columns(2)

    def apply_fix(root_cause):
        if "Webhook" in root_cause:
            company_state["webhook_missing"] = []
        elif "API keys" in root_cause:
            company_state["api_key_invalid"] = []
        elif "Frontend" in root_cause:
            company_state["frontend_not_deployed"] = []
        elif "Environment variables" in root_cause:
            company_state["env_vars_missing"] = []

        with open("data/company_state.json", "w") as f:
            json.dump(company_state, f, indent=2)

    with col1:
        if st.button("✅ Approve"):
            act(agent_state, True)
            apply_fix(agent_state.decision["root_cause"])
            remember(agent_state)
            st.success("Fix applied. System state updated.")

    with col2:
        if st.button("❌ Reject"):
            act(agent_state, False)
            remember(agent_state)
            st.warning("Action rejected.")
