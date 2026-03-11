import asyncio
import streamlit as st

# Import the configured agent from our modular architecture
from src.agent import agent

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Local AI Agent", page_icon="🤖", layout="centered")
st.title("Ollama AI Starter Kit 🚀")
st.caption("Running 100% locally on your machine. No data leaves your computer.")

# --- Chat History Initialization ---
# We use Streamlit's session_state to remember the conversation on the screen
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages when the page reloads
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input & AI Response ---
# st.chat_input displays the text box at the bottom
if prompt := st.chat_input("Ask me anything about code..."):
    
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
                # Stream the response from the local Ollama model
                async with agent.run_stream(user_text) as result:
                    async for full_text_so_far in result.stream_text():
                        final_text = full_text_so_far
                        # Update the UI with a blinking cursor effect
                        message_placeholder.markdown(final_text + "▌")
                
                # Final update without the cursor
                message_placeholder.markdown(final_text)
            except Exception as e:
                st.error(f"Critical Error: Is Ollama running? ({e})")
                
            return final_text

        # Execute the async function and catch the returned response
        full_response = asyncio.run(fetch_ai_response(prompt))
        
    # 3. Save the AI's response to the chat history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})