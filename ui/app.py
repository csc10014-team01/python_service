"""Streamlit chat UI.   Run:  streamlit run ui/app.py      (the API must be running on port 8000)

The UI never imports assistant_core: it only talks to the backend through the HTTP API.
"""
import os
import sys
import uuid
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # so "import ui..." works under streamlit

from ui.api_client import AssistantClient
from ui.logic import EXAMPLES, WELCOME, format_sources, status_note, validate_input

st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
client = AssistantClient(os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000"))

# ---- session state: remembered between reruns of this script ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "rated" not in st.session_state:
    st.session_state.rated = set()

st.title("🎓 FIT Study Assistant")
st.caption("This is an AI assistant. Check important decisions with the Training Office.")
if not client.healthy():
    st.error("Cannot reach the assistant. Please try again when the service is back.")


def rate_answer(request_id: str, rating: int) -> None:
    if request_id in st.session_state.rated:
        return
    if not client.send_feedback(request_id, rating):
        st.session_state.feedback_notice = "Could not save your feedback. Please try again."
        return
    st.session_state.rated.add(request_id)
    st.session_state.feedback_notice = "Thanks for your feedback!"


if notice := st.session_state.pop("feedback_notice", None):
    st.toast(notice)

with st.sidebar:
    st.subheader("Try an example")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex

# ---- history -------------------------------------------------------------------
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            st.caption(m["sources"])
        if m.get("note"):
            st.info(m["note"])
        rid = m.get("request_id")
        if rid and rid not in st.session_state.rated:
            c1, c2 = st.columns(2)
            c1.button("👍 Helpful", key=f"up{i}", on_click=rate_answer, args=(rid, 1))
            c2.button("👎 Not helpful", key=f"down{i}", on_click=rate_answer, args=(rid, -1))

# ---- new question ----------------------------------------------------------------
typed_question = st.chat_input("Ask about fees, offices or the handbook…")
example_question = st.session_state.pop("pending", None)
question = typed_question if typed_question is not None else example_question
if question is not None:
    problem = validate_input(question)
    if problem:
        st.warning(problem)
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Thinking…"):
            result = client.ask(question, st.session_state.session_id)
        if result.ok:
            st.session_state.messages.append({"role": "assistant", "content": result.answer,
                                              "sources": format_sources(result.sources),
                                              "note": status_note(result), "request_id": result.request_id})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
        st.rerun()
