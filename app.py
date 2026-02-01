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
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Agentic AI Support", layout="wide")

# -------------------------------------------------
# ACCESSIBLE PASTEL-GREEN THEME (FIXED CONTRAST)
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #eef7f1;
        color: #1f3d2b;
    }
    header, footer {visibility: hidden;}

    /* ---------- TEXT ---------- */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #1f3d2b !important;
    }

    /* ---------- CONTAINERS ---------- */
    .stContainer {
        background-color: #f9fffb;
        border: 1px solid #cfe8db;
        border-radius: 16px;
        padding: 22px;
        color: #1f3d2b;
    }

    /* ---------- INPUTS ---------- */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #1f3d2b !important;
        border: 1px solid #cfe8db !important;
        border-radius: 10px !important;
    }

    /* ---------- RADIO TABS ---------- */
    .stRadio > div {
        background-color: #f9fffb;
        border: 1px solid #cfe8db;
        border-radius: 14px;
        padding: 8px;
    }

    .stRadio label {
        color: #1f3d2b !important;
        font-weight: 600;
    }

    /* Selected radio */
    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] input:checked + div {
        background-color: #6fbf9a !important;
        border-radius: 10px;
    }

    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] input:checked + div span {
        color: #ffffff !important;
    }

    /* ---------- BUTTONS ---------- */
    .stButton > button {
        background-color: #6fbf9a;
        color: #ffffff !important;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        padding: 10px 22px;
    }

    .stButton > button:hover {
        background-color: #5cad89;
        color: #ffffff !important;
    }

    /* ---------- DATAFRAME ---------- */
    .stDataFrame, .stDataFrame td, .stDataFrame th {
        background-color: #f9fffb !important;
        color: #1f3d2b !important;
        border-color: #cfe8db !important;
    }

    /* ---------- EXPANDERS ---------- */
    details summary {
        background-color: #eef7f1;
        color: #1f3d2b !important;
        border-radius: 10px;
        padding: 8px;
        font-weight: 600;
    }

    /* ---------- METRICS ---------- */
    [data-testid="metric-container"] {
        background-color: #f9fffb;
        border: 1px solid #cfe8db;
        border-radius: 14px;
        padding: 16px;
        color: #1f3d2b;
    }

    /* ---------- ALERTS ---------- */
    .stAlert-success { background-color: #e3f6ed; color: #1f3d2b; }
    .stAlert-warning { background-color: #fff4e5; color: #5a3b00; }
    .stAlert-error   { background-color: #fdecea; color: #611a15; }

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# FEEDBACK LEARNER
# -------------------------------------------------
feedback_learner = FeedbackLearner()

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
    st.markdown("<p style='text-align:center;color:#4f7f69;'>Self-healing support system</p>", unsafe_allow_html=True)

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
# NAVIGATION (VISIBLE TABS)
# =================================================
if st.session_state.role == "user":
    page = st.radio(
        "",
        ["Raise Ticket", "My Tickets"],
        horizontal=True
    )
else:
    page = "Agent Dashboard"

# -------------------------------------------------
# TAXONOMY
# -------------------------------------------------
ISSUES = [
    "Checkout page blank",
    "Payments failing",
    "Payment success but order not created",
    "Cart not updating",
    "Product page not loading",
    "Home page not loading",
    "Search results incorrect",
    "Discounts not applying",
    "Order confirmation email missing",
    "Mobile view broken",
    "Slow page load after migration",
    "Unexpected UI changes after deploy"
]

ERRORS = [
    "Missing webhook",
    "401 API Unauthorized",
    "403 Forbidden",
    "404 Resource Not Found",
    "500 Internal Server Error",
    "API rate limit exceeded",
    "Frontend build not deployed",
    "Environment variables missing",
    "Payment gateway timeout",
    "Invalid API response format",
    "CORS policy blocked request",
    "Other (describe manually)"
]

# =================================================
# USER — RAISE TICKET
# =================================================
if page == "Raise Ticket":
    with st.container():
        st.subheader("Raise a Support Ticket")

        tickets = get_all_tickets()
        merchant_id = f"M{len(tickets)+1:03d}"

        st.markdown(
            f"""
            <div style="
                background-color:#f9fffb;
                border:1px solid #cfe8db;
                border-radius:10px;
                padding:10px;
                font-weight:600;
                color:#1f3d2b;
            ">
                Merchant ID: {merchant_id}
            </div>
            """,
            unsafe_allow_html=True
        )

        issue = st.selectbox("Issue Type", ISSUES)
        error = st.selectbox("Observed Error", ERRORS)

        custom_error = ""
        if error.startswith("Other"):
            custom_error = st.text_area("Describe the error")

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
        st.subheader("My Tickets")

        df = normalize_ticket_df(pd.DataFrame(get_all_tickets()))
        user_df = df[df["created_by"] == st.session_state.username]

        if user_df.empty:
            st.info("No tickets raised yet.")
        else:
            st.dataframe(
                user_df[["ticket_id", "issue", "error", "status", "time"]],
                width="stretch"
            )

# =================================================
# ADMIN — DASHBOARD
# =================================================
if page == "Agent Dashboard":
    with st.container():
        st.subheader("Agent Decision Dashboard")

        df = normalize_ticket_df(pd.DataFrame(get_all_tickets()))
        st.metric("Total Tickets", len(df))
        st.dataframe(df, width="stretch")

        agent_state = AgentState()
        observe(agent_state, df.to_dict("records"))
        reason(agent_state)
        decide(agent_state)

        decision = agent_state.decision

        if decision["status"] != "action_proposed":
            st.info("System stable. No action required.")
        else:
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

        st.subheader("Agent Learning Memory")
        if not feedback_learner.memory:
            st.info("No feedback yet.")
        else:
            for error, actions in feedback_learner.memory.items():
                with st.expander(error):
                    for action, stats in actions.items():
                        st.write(
                            f"Action: {action} | "
                            f"Success: {stats['success']} | "
                            f"Fail: {stats['fail']}"
                        )
