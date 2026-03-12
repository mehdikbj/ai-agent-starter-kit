#!/bin/bash

# Clear the terminal for a clean UI
clear

echo "🚀 Initializing Root AI..."
echo "--------------------------------------"

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# --- 1. CHECK AND INSTALL PYTHON ---
if ! command -v python3 &> /dev/null; then
    echo "⚙️ Python3 is not installed. Trying to install it..."
    if command -v brew &> /dev/null; then
        echo "🍺 Homebrew found. Installing Python3 via brew..."
        brew update
        brew install python@3
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 Linux detected. Installing Python3 via apt-get..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-pip
    else
        echo "❌ Aucune méthode d'installation automatique de Python disponible."
        echo "Installez Python manuellement : https://www.python.org/downloads/"
        exit 1
    fi
    echo "✅ Python3 installé ou déjà présent."
fi

# --- 2. CHECK AND INSTALL OLLAMA ---
if ! command -v ollama &> /dev/null; then
    echo "⚙️ Ollama is not installed. Installing it for you..."
    
    # MAGIC ONE-LINER FOR MAC & LINUX !
    curl -fsSL https://ollama.com/install.sh | sh
    
    echo "⏳ Waiting for Ollama to wake up..."
    sleep 5
fi

# --- 3. ENSURE OLLAMA IS RUNNING ---
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "🔄 Starting Ollama background service..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Ollama
    else
        ollama serve > /dev/null 2>&1 &
    fi
    sleep 5
fi

# --- 3. DOWNLOAD THE AI MODEL (THE BRAIN) ---
MODEL_NAME="llama3.1"
echo "🧠 Checking if model '$MODEL_NAME' is present..."
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "📥 Downloading the AI brain ('$MODEL_NAME')..."
    echo "⚠️ This is a 4.7GB file. Grab a coffee, this might take a while!"
    ollama pull "$MODEL_NAME"
fi

# --- 4. PYTHON ENVIRONMENT SETUP ---
if [ ! -d "venv" ]; then
    echo "📦 Setting up the Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo "✅ Setup complete!"
else
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
fi

# --- 5. RUN THE WEB APP ---
echo "--------------------------------------"
echo "🌐 Opening the Web Application in your browser..."
python3 -m streamlit run main.py

echo "--------------------------------------"
read -p "Press [Enter] to close this window..."