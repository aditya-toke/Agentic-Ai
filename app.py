from db import init_db, insert_ticket, get_all_tickets, update_ticket_status
init_db()

import streamlit as st
import pandas as pd
from datetime import datetime

from agent.feedback import FeedbackLearner
from agent.state import AgentState
from agent.observer import observe
from agent.reasoner import reason
from agent.decider import decide
from agent.actor import act

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(page_title="Agentic AI Support", layout="wide")

# -------------------------------------------------
# Feedback Learner (GLOBAL MEMORY)
# -------------------------------------------------
feedback_learner = FeedbackLearner()

# -------------------------------------------------
# Helpers — BACKWARD COMPATIBILITY
# -------------------------------------------------
def normalize_ticket_df(df):
    if df.empty:
        return df

    if "status" not in df.columns:
        df["status"] = "OPEN"

    if "created_by" not in df.columns:
        df["created_by"] = "unknown"

    return df

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# -------------------------------------------------
# Authentication
# -------------------------------------------------
def authenticate(username, password):
    if username == "admin" and password == "admin123":
        return True, "admin"
    if username == "user" and password == "user123":
        return True, "user"
    return False, None

# =================================================
# LOGIN PAGE
# =================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <h1 style="text-align:center;color:#1b5e3c;">🧠 Agentic AI Support</h1>
        <p style="text-align:center;color:#4f8f6f;">
        Intelligent self-healing support for modern commerce
        </p>
        """,
        unsafe_allow_html=True
    )

    _, center, _ = st.columns([1.2, 1, 1.2])
    with center:
        with st.container(border=True):
            st.subheader("Sign in")

            username = st.text_input("Username", placeholder="admin or user")
            password = st.text_input("Password", type="password")

            if st.button("Sign in", type="primary"):
                success, role = authenticate(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    st.stop()

# =================================================
# LOGOUT
# =================================================
_, col = st.columns([6, 1])
with col:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =================================================
# ROLE-BASED NAVIGATION
# =================================================
if st.session_state.role == "user":
    page = st.radio("User Menu", ["📝 Raise Ticket", "📄 My Tickets"], horizontal=True)
else:
    page = "📊 Agent Dashboard"

# -------------------------------------------------
# Shared Taxonomy
# -------------------------------------------------
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

# =================================================
# USER — RAISE TICKET
# =================================================
if page == "📝 Raise Ticket":
    st.title("📝 Raise a Support Ticket")

    tickets = get_all_tickets()
    merchant_id = f"M{len(tickets)+1:03d}"

    st.text_input("Merchant ID", merchant_id, disabled=True)

    issue = st.selectbox("Issue Type", ISSUES)
    error = st.selectbox("Observed Error", ERRORS)

    custom_error = ""
    if error.startswith("Other"):
        custom_error = st.text_area("Describe the error")

    description = st.text_area("Additional context")

    if st.button("📨 Submit Ticket"):
        final_error = custom_error if error.startswith("Other") else error

        if not final_error.strip():
            st.warning("Please describe the error")
        else:
            insert_ticket({
                "ticket_id": f"T{len(tickets)+1}",
                "merchant_id": merchant_id,
                "issue": issue,
                "error": final_error,
                "context": description,
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "OPEN",
                "created_by": st.session_state.username
            })
            st.success("Ticket submitted successfully (Status: OPEN)")

# =================================================
# USER — MY TICKETS (LOADS FROM DB)
# =================================================
if page == "📄 My Tickets":
    st.title("📄 My Tickets")

    tickets = get_all_tickets()
    df = normalize_ticket_df(pd.DataFrame(tickets))

    # Filter tickets raised by current user
    user_df = df[df["created_by"] == st.session_state.username]

    if user_df.empty:
        st.info("You have not raised any tickets yet.")
        st.stop()

    st.dataframe(
        user_df[
            ["ticket_id", "merchant_id", "issue", "error", "status", "time"]
        ],
        use_container_width=True
    )

# =================================================
# ADMIN — AGENT DASHBOARD
# =================================================
if page == "📊 Agent Dashboard":
    st.title("📊 Agentic AI – Decision Dashboard")

    tickets = get_all_tickets()
    df = normalize_ticket_df(pd.DataFrame(tickets))

    st.metric("🚨 Total Tickets", len(df))
    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.stop()

    agent_state = AgentState()
    observe(agent_state, df.to_dict("records"))
    reason(agent_state)
    decide(agent_state)

    decision = agent_state.decision

    if decision["status"] != "action_proposed":
        st.info("No actionable issue detected")
        st.stop()

    st.subheader("⚖️ Admin Approval Required")
    st.warning(f"Root cause detected: {decision['root_cause']}")

    for _, row in df.iterrows():
        if row["status"] == "OPEN":

            c1, c2 = st.columns(2)

            with c1:
                if st.button(f"✅ Approve {row['ticket_id']}"):
                    update_ticket_status(row["ticket_id"], "APPROVED")
                    feedback_learner.record_feedback(
                        row["error"], decision["action"], True
                    )
                    st.rerun()

            with c2:
                if st.button(f"❌ Reject {row['ticket_id']}"):
                    update_ticket_status(row["ticket_id"], "REJECTED")
                    feedback_learner.record_feedback(
                        row["error"], decision["action"], False
                    )
                    st.rerun()

    # -------------------------------------------------
    # Agent Learning Memory
    # -------------------------------------------------
    st.subheader("📚 Agent Learning Memory")

    if not feedback_learner.memory:
        st.info("No feedback recorded yet.")
    else:
        for error, actions in feedback_learner.memory.items():
            with st.expander(f"Error: {error}"):
                for action, stats in actions.items():
                    total = stats["success"] + stats["fail"]
                    rate = stats["success"] / total if total else 0
                    st.write(
                        f"""
                        **Action:** {action}  
                        Success: {stats['success']}  
                        Fail: {stats['fail']}  
                        Success Rate: {rate:.2f}
                        """
                    )
