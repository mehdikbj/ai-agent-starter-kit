# 🚀 Ollama AI Starter Kit (Privacy-First)

Welcome to the **Ollama AI Starter Kit**! 
This project provides a ready-to-use foundation for building your own local AI assistant. Say goodbye to expensive subscriptions and data privacy concerns: this Starter Kit runs a Large Language Model (LLM) directly on your machine's silicon.



## ✨ Key Features

* **🔒 100% Local & Private:** Your data and conversations never leave your machine. Perfect for analyzing proprietary code or confidential documents.
* **💸 Zero API Costs:** Chat limitlessly without ever pulling out your credit card.
* **🪄 Magic 1-Click Install:** Smart scripts for both Mac/Linux and Windows that automatically download Ollama, fetch the model, set up the Python environment, and launch the application for you.
* **🎨 Modern Web UI:** A fluid, ChatGPT-style conversational interface built instantly with **Streamlit**.
* **🏗️ Modular Architecture (Pro):** Built on top of **PydanticAI**. The codebase is cleanly separated (`config.py`, `agent.py`, `main.py`) so you can easily add new tools (RAG, Web Search) as your project scales.

---

## 📖 User Manual

This project was designed to be accessible to everyone, even without a deep technical background.

### Step 1: Download the project
Download this repository to your computer and open the folder.

### Step 2: Grant permission (Mac & Linux ONLY)
*If you are on Windows, you can skip this step!*
For security reasons, macOS and Linux require you to grant permission before running a new script. 
1. Open the **Terminal** app.
2. Type the following command (don't forget the space at the end!): `chmod +x `
3. Drag and drop the `start_mac.command` file from your Finder into the Terminal window.
4. Press **Enter**.

### Step 3: Launch the AI (The Magic Double-Click)
Depending on your operating system, simply double-click the corresponding file:

* 🍏 **Mac / 🐧 Linux:** Double-click on `start_mac.command`
* 🪟 **Windows:** Double-click on `start_windows.bat`

The script will handle everything automatically:
1. Check if **Ollama** is installed (and install it if it isn't).
2. Download the AI "brain" (the 4.7GB `llama3.1` model). *Note: This step may take a few minutes depending on your internet connection.*
3. Create an isolated Python environment and install all necessary libraries.
4. Automatically open the Web Chat interface in your default browser!

> 💡 **Tip:** Keep the small black terminal window open in the background while you chat in your browser. It acts as the engine powering your AI!

---

## 📂 Code Architecture (For Developers)

If you want to modify or upgrade the assistant, here is how the codebase is structured:

* `start_mac.command` / `start_windows.bat`: The auto-installer and launch scripts.
* `main.py`: The Web User Interface built with Streamlit.
* `requirements.txt`: The list of Python dependencies (PydanticAI, Streamlit, etc.).
* `src/`: The core business logic.
  * `config.py`: Tricks the OpenAI SDK into connecting to your local machine.
  * `agent.py`: The AI Agent definition. **This is where you can edit the default System Prompt!**

## 🛠️ How to Customize Your AI

1. **Change its personality dynamically:** Open the Web UI and use the left sidebar to change the AI's persona in real-time (e.g., "Act as a Senior Lawyer", "You are a Python Expert").
2. **Change the default prompt:** Open `src/agent.py` and modify the `DEFAULT_SYSTEM_PROMPT` variable to permanently change how the AI behaves on startup.
3. **Change the model:** By default, the kit uses `llama3.1`. You can change this by creating a `.env` file in the root directory and adding: `MODEL_ID=phi3` (or any other model available on the Ollama library).