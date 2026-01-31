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

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Agentic AI Support", layout="wide")

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# ---------------- Authentication ----------------
def authenticate(username, password):
    if username == "admin" and password == "admin123":
        return True, "admin"
    if username == "user" and password == "user123":
        return True, "user"
    return False, None

# ==================================================
# LOGIN PAGE
# ==================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <h1 style="text-align:center; color:#1b5e3c;">🧠 Agentic AI Support</h1>
        <p style="text-align:center; color:#4f8f6f;">
        Intelligent self-healing support for modern commerce
        </p>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1.2, 1, 1.2])

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
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    st.stop()

# ==================================================
# LOGOUT
# ==================================================
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

# ==================================================
# ROLE-BASED NAVIGATION
# ==================================================
if st.session_state.role == "user":
    page = st.radio(
        "User Menu",
        ["📝 Raise Ticket", "📄 My Tickets"],
        horizontal=True
    )
else:
    page = "📊 Agent Dashboard"

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
# USER — RAISE TICKET
# ==================================================
if page == "📝 Raise Ticket":
    st.title("📝 Raise a Support Ticket")

    tickets = get_all_tickets()
    merchant_id = f"M{len(tickets)+1:03d}"

    st.text_input("Merchant ID", merchant_id, disabled=True)

    issue = st.selectbox("Issue Type", ISSUES)
    error = st.selectbox("Observed Error", ERRORS)

    custom_error = ""
    if error == "Other (describe manually)":
        custom_error = st.text_area("Describe the error", max_chars=200)

    description = st.text_area("Additional context (optional)", max_chars=300)

    if st.button("📨 Submit Ticket"):
        final_error = custom_error if error.startswith("Other") else error

        if not final_error.strip():
            st.warning("Please describe the error")
        else:
            ticket = {
                "ticket_id": f"T{len(tickets)+1}",
                "merchant_id": merchant_id,
                "issue": issue,
                "error": final_error,
                "context": description,
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "OPEN",
                "created_by": st.session_state.username
            }
            insert_ticket(ticket)
            st.success("Ticket submitted successfully (Status: OPEN)")

# ==================================================
# USER — MY TICKETS (FETCHED FROM DB)
# ==================================================
if page == "📄 My Tickets":
    st.title("📄 My Tickets")

    tickets = get_all_tickets()
    df = pd.DataFrame(tickets)

    # Filter only logged-in user's tickets
    user_df = df[df["created_by"] == st.session_state.username]

    if user_df.empty:
        st.info("You have not raised any tickets yet.")
        st.stop()

    st.dataframe(
        user_df[
            ["ticket_id", "issue", "error", "status", "time"]
        ],
        use_container_width=True
    )

    st.subheader("🧠 AI Suggested Solutions")

    for _, row in user_df.iterrows():
        with st.expander(f"{row['ticket_id']} — {row['status']}"):
            st.write(f"**Issue:** {row['issue']}")
            st.write(f"**Error:** {row['error']}")

            if "webhook" in row["error"].lower():
                solution = "Ensure webhook endpoints are configured and reachable."
            elif "401" in row["error"]:
                solution = "Verify API keys and permissions."
            elif "frontend" in row["error"].lower():
                solution = "Redeploy frontend build and verify assets."
            else:
                solution = "Investigate recent configuration changes."

            st.success(solution)

            if row["status"] == "OPEN":
                st.info("Awaiting admin review")
            elif row["status"] == "APPROVED":
                st.success("Approved by admin")
            elif row["status"] == "REJECTED":
                st.error("Rejected by admin")

# ==================================================
# ADMIN — AGENT DASHBOARD (FETCHES ALL TICKETS)
# ==================================================
if page == "📊 Agent Dashboard":
    st.title("📊 Agentic AI – Decision Dashboard")

    tickets = get_all_tickets()
    df = pd.DataFrame(tickets)

    st.metric("🚨 Total Tickets", len(df))
    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.stop()

    agent_state = AgentState()
    observe(agent_state, tickets)
    reason(agent_state)
    decide(agent_state)

    decision = agent_state.decision

    if decision["status"] in ["no_action", "blocked"]:
        st.info("No actionable issue detected")
        st.stop()

    st.subheader("⚖️ Admin Approval Required")
    st.warning(f"Root cause detected: {decision['root_cause']}")

    for _, row in df.iterrows():
        if row["error"] == decision["root_cause"] and row["status"] == "OPEN":

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"✅ Approve {row['ticket_id']}"):
                    update_ticket_status(row["ticket_id"], "APPROVED")
                    st.success("Ticket approved")
                    st.rerun()

            with col2:
                if st.button(f"❌ Reject {row['ticket_id']}"):
                    update_ticket_status(row["ticket_id"], "REJECTED")
                    st.warning("Ticket rejected")
                    st.rerun()
