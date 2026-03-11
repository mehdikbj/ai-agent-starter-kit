import asyncio
import streamlit as st

# Import the configured agent and its default prompt from our modular architecture
from src.agent import agent, DEFAULT_SYSTEM_PROMPT

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Root AI", page_icon="🤖", layout="wide")

# ==========================================
# 🎛️ SIDEBAR: Settings & Controls
# ==========================================
with st.sidebar:
    st.header("⚙️ AI Settings")
    
    # Dynamic System Prompt using the developer's default as the starting value
    system_prompt = st.text_area(
        "AI Persona (System Prompt):", 
        value=DEFAULT_SYSTEM_PROMPT, 
        height=200,
        help="Change this text to modify the AI's behavior (e.g., 'Act as a pirate', 'You are a Python expert...')."
    )
    
    st.divider() # Adds a nice horizontal line
    
    # Clear Memory Button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.message_history = []
        st.rerun() # Magically refreshes the UI instantly

# ==========================================
# 💬 MAIN CHAT INTERFACE
# ==========================================
st.title("Root AI 🚀")
st.caption("Running 100% locally on your machine. No data leaves your computer.")

# --- Chat History & AI Memory Initialization ---
# 1. UI Memory (For Streamlit to draw the chat on screen)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. AI Memory (For PydanticAI to understand the context)
if "message_history" not in st.session_state:
    st.session_state.message_history = []

# Display all previous messages when the page reloads
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input & AI Response ---
# st.chat_input displays the text box at the bottom
if prompt := st.chat_input("Ask me anything..."):
    
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Display Assistant Response with Streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Cleaner approach: The async function returns the final string
        async def fetch_ai_response(user_text: str) -> str:
            final_text = ""
            try:
                # 🧠 MAGIC: We pass the sidebar's system_prompt via `deps=`
                # and the conversation history via `message_history=`
                async with agent.run_stream(
                    user_text, 
                    deps=system_prompt,
                    message_history=st.session_state.message_history
                ) as result:
                    async for full_text_so_far in result.stream_text():
                        final_text = full_text_so_far
                        # Update the UI with a blinking cursor effect
                        message_placeholder.markdown(final_text + "▌")
                
                # Final update without the cursor
                message_placeholder.markdown(final_text)
                
                # 💾 CRITICAL: Update the AI's memory with this new exchange
                st.session_state.message_history = result.all_messages()
                
            except Exception as e:
                st.error(f"Critical Error: Is Ollama running? ({e})")
                
            return final_text

        # Execute the async function and catch the returned response
        full_response = asyncio.run(fetch_ai_response(prompt))
        
    # 3. Save the AI's response to the UI history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})