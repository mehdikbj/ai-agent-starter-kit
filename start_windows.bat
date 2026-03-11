@echo off
title Ollama AI Starter Kit
cls

echo ==========================================
echo 🚀 Initializing Root AI...
echo ==========================================
echo.

:: 1. NAVIGATE TO SCRIPT FOLDER
:: This ensures the script runs in the correct directory even if run as admin
cd /d "%~dp0"

:: 2. CHECK AND INSTALL OLLAMA
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚙️ Ollama is not installed. Downloading it for you...
    echo 📥 Fetching Windows Installer...
    curl -L https://ollama.com/download/OllamaSetup.exe -o OllamaSetup.exe
    
    echo 📦 Running installer... (Please follow the prompts on your screen)
    start /wait OllamaSetup.exe
    
    echo 🧹 Cleaning up...
    del OllamaSetup.exe
    
    echo ⏳ Waiting 5 seconds for Ollama to register...
    timeout /t 5 /nobreak >nul
)

:: 3. ENSURE OLLAMA IS RUNNING
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 🔄 Starting Ollama background service...
    :: We start the Ollama tray application silently in the background
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    echo ⏳ Waiting 5 seconds for the engine to warm up...
    timeout /t 5 /nobreak >nul
)

:: 4. DOWNLOAD THE AI MODEL (THE BRAIN)
set MODEL_NAME=llama3.1
echo 🧠 Checking if model '%MODEL_NAME%' is present...
ollama list | findstr /i "%MODEL_NAME%" >nul
if %ERRORLEVEL% neq 0 (
    echo 📥 Downloading the AI brain ('%MODEL_NAME%')...
    echo ⚠️ This is a 4.7GB file. Grab a coffee, this might take a while!
    ollama pull %MODEL_NAME%
)

:: 5. PYTHON ENVIRONMENT SETUP
if not exist venv\Scripts\activate.bat (
    echo 📦 First run detected. Setting up the Python environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ⏳ Installing dependencies (this might take a minute)...
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo ✅ Setup complete!
) else (
    echo 🔄 Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: 6. RUN THE WEB APP
echo.
echo ==========================================
echo 🌐 Opening the Web Application in your browser...
echo 💡 Tip: Keep this terminal open while using the app.
echo ==========================================
python -m streamlit run main.py

:: Keep terminal open if app crashes
echo.
pause