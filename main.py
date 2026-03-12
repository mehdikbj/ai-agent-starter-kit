import asyncio

import httpx
import streamlit as st

from src.agent import DEFAULT_SYSTEM_PROMPT, AgentDeps, get_agent
from src import rag

st.set_page_config(page_title="Root AI", page_icon="🤖", layout="wide")


@st.cache_data(ttl=30)
def get_installed_models() -> list[str]:
    """
    Fetches the list of locally installed Ollama models via the Ollama REST API.
    Falls back to a safe default if Ollama is not reachable.
    """
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            if models:
                return models
    except Exception:
        pass
    return ["llama3.1"]


with st.sidebar:
    st.header("⚙️ AI Settings")

    # --- Model Selector ---
    models = get_installed_models()
    selected_model = st.selectbox(
        "🧠 Model",
        options=models,
        help="Lists all models currently installed in Ollama. "
             "Run `ollama pull <model>` in your terminal to add more.",
    )

    # Reset conversation history when the user switches models so that
    # message format stays consistent with the active model.
    if st.session_state.get("active_model") != selected_model:
        st.session_state.active_model = selected_model
        st.session_state.messages = []
        st.session_state.message_history = []

    # --- System Prompt ---
    system_prompt = st.text_area(
        "AI Persona (System Prompt):",
        value=DEFAULT_SYSTEM_PROMPT,
        height=150,
        help="Change this to modify the AI's behavior "
             "(e.g., 'Act as a pirate', 'You are a Python expert...').",
    )

    st.divider()

    # --- RAG: Document Upload ---
    st.subheader("📄 Document Context (RAG)")
    st.caption("Upload PDFs to let the AI answer questions about their content.")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            state_key = f"rag_indexed_{uploaded_file.name}"
            if state_key not in st.session_state:
                with st.spinner(f"Indexing {uploaded_file.name}…"):
                    chunk_count = rag.index_pdf(uploaded_file.read(), uploaded_file.name)
                    st.session_state[state_key] = chunk_count
                st.success(f"✅ {uploaded_file.name}: {st.session_state[state_key]} chunks")

    doc_count = rag.document_count()
    if doc_count > 0:
        st.caption(f"📚 {doc_count} chunks in memory")
        if st.button("🗑️ Clear Document Index", use_container_width=True):
            rag.clear_index()
            for key in [k for k in st.session_state if k.startswith("rag_indexed_")]:
                del st.session_state[key]
            st.rerun()

    st.divider()

    # --- Chat Controls ---
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.message_history = []
            st.rerun()
    with ctrl_col2:
        if st.session_state.get("messages"):
            chat_export = "\n\n".join(
                f"**{m['role'].capitalize()}:** {m['content']}"
                for m in st.session_state.messages
            )
            st.download_button(
                "💾 Export",
                data=chat_export,
                file_name="chat_history.md",
                mime="text/markdown",
                use_container_width=True,
            )


st.title("Root AI 🚀")
st.caption("Running 100% locally on your machine. No data leaves your computer.")

# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_history" not in st.session_state:
    st.session_state.message_history = []
if "active_model" not in st.session_state:
    st.session_state.active_model = selected_model

# --- Render Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input & AI Response ---
if prompt := st.chat_input("Ask me anything..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        async def fetch_ai_response(user_text: str) -> str:
            final_text = ""
            try:
                # Retrieve relevant document chunks; empty string when no docs indexed.
                context = rag.retrieve_context(user_text)
                deps = AgentDeps(system_prompt=system_prompt, rag_context=context)
                active_agent = get_agent(selected_model)

                async with active_agent.run_stream(
                    user_text,
                    deps=deps,
                    message_history=st.session_state.message_history,
                ) as result:
                    async for chunk in result.stream_text():
                        final_text = chunk
                        # Live update with a blinking cursor effect
                        message_placeholder.markdown(final_text + "▌")

                # Final render without cursor
                message_placeholder.markdown(final_text)

                # Persist the full exchange in PydanticAI's message format
                st.session_state.message_history = result.all_messages()

            except Exception as e:
                st.error(f"Critical Error: Is Ollama running? ({e})")

            return final_text

        # Create a fresh event loop to avoid conflicts with Streamlit's uvloop.
        loop = asyncio.new_event_loop()
        try:
            full_response = loop.run_until_complete(fetch_ai_response(prompt))
        finally:
            loop.close()

    # 3. Save the response to the UI history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})