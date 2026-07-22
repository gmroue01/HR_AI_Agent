import streamlit as st
from backend.auth import login
from chatbot_core import run_agent_turn, SYSTEM_PROMPT

st.set_page_config(page_title="HR_AGENT")

if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [SYSTEM_PROMPT]


def show_login():
    st.title("Login")
    with st.form("login_form"):
        surname = st.text_input("Surname").strip()
        name = st.text_input("Name").strip()
        submitted = st.form_submit_button("Login")
        if submitted:
            user = login(surname, name)
            if user is not None:
                st.session_state.user_role = user["role"]
                st.session_state.username = f"{user['name']} {user['surname']}"
                st.session_state.employee_id = user["id"]
                st.rerun()
            else:
                st.error("No Employee found")


def show_chat():
    st.title("HR Agent")
    st.caption(
        f"Hello **{st.session_state.username}**. You are the ({st.session_state.user_role})")

    if st.button("Disconnect"):
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.chat_history = [SYSTEM_PROMPT]
        st.rerun()

    for msg in st.session_state.chat_history:
        if msg["role"] in ("user", "assistant") and msg.get("content"):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("Thinking..."):
            updated_history, reply, trace = run_agent_turn(
                st.session_state.chat_history, user_input, st.session_state.user_role, employee_id=st.session_state.employee_id
            )
        st.session_state.chat_history = updated_history
        with st.chat_message("assistant"):
            st.markdown(reply)
        with st.expander("Debug trace"):
            st.json(trace)


if st.session_state.user_role is None:
    show_login()
else:

    show_chat()
