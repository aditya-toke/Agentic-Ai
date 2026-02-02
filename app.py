from db import init_db, insert_ticket, get_all_tickets, update_ticket_status
init_db()

import streamlit as st
import pandas as pd
from datetime import datetime

from agent.state import AgentState
from agent.observer import observe
from agent.reasoner import reason
from agent.decider import decide
from agent.actor import act
from agent.feedback import FeedbackLearner

# -------------------------------------------------
# SESSION-BASED FEEDBACK LEARNER (SINGLE SOURCE)
# -------------------------------------------------
if "feedback_learner" not in st.session_state:
    st.session_state.feedback_learner = FeedbackLearner()

feedback_learner = st.session_state.feedback_learner

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Agentic AI Support", layout="wide")

# -------------------------------------------------
# ACCESSIBLE PASTEL-GREEN THEME
# -------------------------------------------------
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #eef7f1;
        color: #1f3d2b;
    }
    header, footer {visibility: hidden;}

    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #1f3d2b !important;
    }

    .stContainer {
        background-color: #f9fffb;
        border: 1px solid #cfe8db;
        border-radius: 16px;
        padding: 22px;
    }

    input, textarea, select {
        background-color: #ffffff !important;
        color: #1f3d2b !important;
        border: 1px solid #cfe8db !important;
        border-radius: 10px !important;
    }

    .stButton > button {
        background-color: #6fbf9a;
        color: #ffffff !important;
        border-radius: 12px;
        font-weight: 600;
    }

    .stDataFrame td, .stDataFrame th {
        background-color: #f9fffb !important;
        color: #1f3d2b !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# HELPERS
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
# SESSION STATE
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# -------------------------------------------------
# AUTH
# -------------------------------------------------
def authenticate(username, password):
    if username == "admin" and password == "admin123":
        return True, "admin"
    if username == "user" and password == "user123":
        return True, "user"
    return False, None

# =================================================
# LOGIN
# =================================================
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>Agentic AI Support</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Self-healing support system</p>", unsafe_allow_html=True)

    _, center, _ = st.columns([1.6, 1, 1.6])
    with center:
        with st.container():
            st.subheader("Sign in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Sign in"):
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
_, logout_col = st.columns([6, 1])
with logout_col:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# =================================================
# NAVIGATION
# =================================================
if st.session_state.role == "user":
    page = st.radio("", ["Raise Ticket", "My Tickets"], horizontal=True)
else:
    page = "Agent Dashboard"

# -------------------------------------------------
# USER — RAISE TICKET
# -------------------------------------------------
if page == "Raise Ticket":
    with st.container():
        st.subheader("Raise a Support Ticket")

        tickets = get_all_tickets()
        merchant_id = f"M{len(tickets)+1:03d}"

        st.markdown(f"**Merchant ID:** `{merchant_id}`")

        issue = st.selectbox("Issue Type", [
            "Checkout page blank", "Payments failing", "Cart not updating",
            "Order confirmation missing", "Slow page load", "Mobile UI broken",
            "Discount not applied", "Search not working", "API timeout",
            "Unexpected UI changes"
        ])

        error = st.selectbox("Observed Error", [
            "Missing webhook", "401 API Unauthorized", "500 Internal Server Error",
            "Frontend build not deployed", "CORS blocked", "Invalid API response",
            "Rate limit exceeded", "Env variables missing", "Gateway timeout",
            "Other (describe manually)"
        ])

        custom_error = st.text_area("Describe error") if error.startswith("Other") else ""
        description = st.text_area("Additional context")

        if st.button("Submit Ticket"):
            insert_ticket({
                "ticket_id": f"T{len(tickets)+1}",
                "merchant_id": merchant_id,
                "issue": issue,
                "error": custom_error if error.startswith("Other") else error,
                "context": description,
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "OPEN",
                "created_by": st.session_state.username
            })
            st.success("Ticket submitted successfully")

# =================================================
# USER — MY TICKETS
# =================================================
if page == "My Tickets":
    with st.container():
        df = normalize_ticket_df(pd.DataFrame(get_all_tickets()))
        user_df = df[df["created_by"] == st.session_state.username]

        if user_df.empty:
            st.info("No tickets raised yet.")
        else:
            st.dataframe(user_df[["ticket_id", "issue", "error", "status", "time"]], width="stretch")

# =================================================
# ADMIN — DASHBOARD
# =================================================
if page == "Agent Dashboard":
    with st.container():
        df = normalize_ticket_df(pd.DataFrame(get_all_tickets()))
        st.metric("Total Tickets", len(df))
        st.dataframe(df, width="stretch")

        agent_state = AgentState()
        observe(agent_state, df.to_dict("records"))
        reason(agent_state)
        decide(agent_state)

        decision = agent_state.decision

        if decision["status"] == "action_proposed":
            st.warning(f"Root Cause: {decision['root_cause']}")

            for _, row in df.iterrows():
                if row["status"] == "OPEN":
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"Approve {row['ticket_id']}"):
                            update_ticket_status(row["ticket_id"], "APPROVED")
                            feedback_learner.record_feedback(row["error"], decision["action"], True)
                            st.rerun()
                    with c2:
                        if st.button(f"Reject {row['ticket_id']}"):
                            update_ticket_status(row["ticket_id"], "REJECTED")
                            feedback_learner.record_feedback(row["error"], decision["action"], False)
                            st.rerun()

        st.subheader("📚 Agent Learning Memory")

        memory = feedback_learner.get_stats()

        if not memory:
            st.info("No feedback recorded yet.")
        else:
            for error, actions in memory.items():
                with st.expander(f"Error: {error}"):
                    for action, stats in actions.items():
                        total = stats["success"] + stats["fail"]
                        rate = stats["success"] / total if total else 0
                        st.write(
                            f"""
                            **Action:** {action}  
                            ✅ Success: {stats['success']}  
                            ❌ Fail: {stats['fail']}  
                            📊 Success Rate: {rate:.2f}
                            """
                        )
