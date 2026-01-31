from db import init_db, insert_ticket, get_all_tickets
init_db()

import streamlit as st
import pandas as pd
from datetime import datetime

from agent.state import AgentState
from agent.observer import observe
from agent.reasoner import reason
from agent.decider import decide
from agent.actor import act

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Agentic AI Support", layout="wide")

# ---------------- Sidebar Navigation ----------------
page = st.sidebar.radio(
    "Navigate",
    ["📝 Raise Ticket", "📊 Agent Dashboard"]
)

# ---------------- Shared Taxonomy ----------------
ISSUES = [
    "Checkout page blank",
    "Payments failing",
    "Home page not loading"
]

ERRORS = [
    "Missing webhook",
    "401 API Unauthorized",
    "Frontend build not deployed",
    "Other (describe manually)"
]

# ==================================================
# PAGE 1 — RAISE TICKET
# ==================================================
if page == "📝 Raise Ticket":
    st.title("📝 Raise a Support Ticket")

    st.info(
        "This form captures merchant issues. "
        "The AI agent will analyze patterns and suggest actions, "
        "but **will not take action without human approval**."
    )

    tickets = get_all_tickets()

    merchant_id = f"M{len(tickets)+1:03d}"
    st.text_input("Merchant ID", merchant_id, disabled=True)

    issue = st.selectbox("Issue Type", ISSUES)
    error = st.selectbox("Observed Error", ERRORS)

    custom_error = ""
    if error == "Other (describe manually)":
        custom_error = st.text_area(
            "Describe the error (optional)",
            max_chars=200,
            placeholder="Describe unusual or unclear behavior"
        )

    description = st.text_area(
        "Additional context (optional)",
        max_chars=300,
        placeholder="What changed? When did it start?"
    )

    if st.button("📨 Submit Ticket"):
        final_error = custom_error if error.startswith("Other") else error

        if not final_error.strip():
            st.warning("Please describe the error when selecting 'Other'")
        else:
            ticket = {
                "ticket_id": f"T{len(tickets)+1}",
                "merchant_id": merchant_id,
                "issue": issue,
                "error": final_error,
                "context": description,
                "time": datetime.now().strftime("%H:%M:%S")
            }

            insert_ticket(ticket)
            st.success("Ticket submitted successfully")

# ==================================================
# PAGE 2 — AGENT DASHBOARD
# ==================================================
if page == "📊 Agent Dashboard":
    st.title("📊 Agentic AI – Decision Dashboard")

    tickets = get_all_tickets()
    df = pd.DataFrame(tickets)

    # ---------------- Metrics ----------------
    st.metric("🚨 Total Tickets", len(tickets))

    # ---------------- Latest Tickets ----------------
    st.subheader("📩 Latest Tickets")
    if tickets:
        st.dataframe(df.tail(5), use_container_width=True)
    else:
        st.info("No tickets raised yet")

    if not tickets:
        st.stop()

    # ---------------- Agent Loop ----------------
    agent_state = AgentState()
    observe(agent_state, tickets)
    reason(agent_state)
    decide(agent_state)

    # ---------------- Pattern Detection ----------------
    st.subheader("📈 Observed Patterns (Evidence)")
    pattern = df["error"].value_counts()
    st.bar_chart(pattern)

    # ---------------- Agent Belief ----------------
    st.subheader("🧠 What the Agent Believes")

    for h in agent_state.hypotheses:
        with st.expander(h["cause"]):
            st.write("Why the agent believes this:")
            st.write(f"- Seen in **{h['blast_radius']}** tickets")
            st.write(f"- Confidence: **{h['confidence']}**")
            st.write(f"- Risk level: **{h['risk']}**")

            if h["confidence"] < 0.6:
                st.warning("⚠️ Low confidence — limited evidence")

    # ---------------- Decision ----------------
    st.subheader("⚖️ Proposed Action & Impact")

    decision = agent_state.decision

    if decision["status"] == "no_action":
        st.success("System appears stable. No action recommended.")

    elif decision["status"] == "blocked":
        st.error(decision["reason"])

    else:
        st.warning(decision["root_cause"])

        st.markdown("**Proposed impact:**")
        st.markdown(
            "- May affect **live checkouts**\n"
            "- Could impact **merchant trust**\n"
            "- Action is **reversible**\n"
            "- No automatic execution"
        )

        st.markdown(
            f"**Confidence:** {decision['confidence']}  \n"
            f"**Risk level:** {decision['risk']}"
        )

        st.info(
            "Ethical safeguard: This system will not "
            "execute changes affecting money or live traffic "
            "without explicit human approval."
        )

        if st.button("✅ Approve Mitigation"):
            act(agent_state, True)
            st.success("Mitigation approved (simulation only)")

        if st.button("❌ Reject"):
            act(agent_state, False)
            st.warning("Action rejected by human operator")
