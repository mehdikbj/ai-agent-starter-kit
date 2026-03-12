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

    # GPU acceleration — behaviour differs per platform:
    #   macOS Apple Silicon → Metal is used automatically by Ollama (no config needed)
    #   macOS Intel         → CPU only (no GPU acceleration available)
    #   Linux NVIDIA        → CUDA used automatically; OLLAMA_NUM_GPU in .env for fine control
    if [[ "$OSTYPE" == "darwin"* ]]; then
        ARCH=$(uname -m)
        if [[ "$ARCH" == "arm64" ]]; then
            echo "🍎 Apple Silicon detected — Metal GPU acceleration is ON automatically."
        else
            echo "💻 Intel Mac detected — running on CPU (no GPU acceleration available)."
        fi
        # Try the desktop .app first; fall back to CLI ollama serve.
        if open -a Ollama 2>/dev/null; then
            echo "   ↳ Ollama.app launched."
        else
            ollama serve > /dev/null 2>&1 &
            echo "   ↳ Ollama CLI started in background."
        fi
    else
        # Linux: load optional NVIDIA override from .env
        if [ -f ".env" ]; then
            export $(grep -E '^OLLAMA_NUM_GPU=' .env | xargs) 2>/dev/null
        fi

        # The curl|sh installer places a CUDA-enabled binary at /usr/local/bin/ollama.
        # Homebrew installs a CPU-only build that may appear first in PATH.
        # Prefer the system binary explicitly when an NVIDIA GPU is present.
        SYSTEM_OLLAMA="/usr/local/bin/ollama"
        if command -v nvidia-smi &> /dev/null; then
            GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
            if [ -n "$GPU_NAME" ]; then
                echo "🎮 NVIDIA GPU detected: $GPU_NAME"
                if [ "$OLLAMA_NUM_GPU" = "0" ]; then
                    echo "   ↳ GPU disabled by OLLAMA_NUM_GPU=0 in .env (CPU only)."
                    ollama serve > /dev/null 2>&1 &
                elif [ -x "$SYSTEM_OLLAMA" ]; then
                    echo "   ↳ Using CUDA-enabled Ollama ($SYSTEM_OLLAMA) — GPU is ON."
                    [ -n "$OLLAMA_NUM_GPU" ] && echo "   ↳ GPU layers: OLLAMA_NUM_GPU=$OLLAMA_NUM_GPU"
                    "$SYSTEM_OLLAMA" serve > /dev/null 2>&1 &
                else
                    echo "   ↳ GPU acceleration is ON (auto)."
                    ollama serve > /dev/null 2>&1 &
                fi
            else
                echo "💻 No NVIDIA GPU detected — running on CPU."
                ollama serve > /dev/null 2>&1 &
            fi
        else
            echo "💻 No NVIDIA GPU detected — running on CPU."
            ollama serve > /dev/null 2>&1 &
        fi
    fi
    sleep 5
fi

# --- 3. DOWNLOAD THE AI MODEL (THE BRAIN) ---
# Read MODEL_ID from .env if set, otherwise default to llama3.1
if [ -f ".env" ]; then
    ENV_MODEL=$(grep -E '^MODEL_ID=' .env | cut -d'=' -f2 | tr -d '[:space:]')
fi
MODEL_NAME="${ENV_MODEL:-llama3.1}"
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