@echo off
:: Force l'encodage UTF-8 pour éviter les caractères bizarres
chcp 65001 >nul
title Root AI
cls

echo ==========================================
echo 🚀 Initializing Root AI...
echo ==========================================
echo.

cd /d "%~dp0"

:: 1. CHECK AND INSTALL OLLAMA
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚙️ Ollama is not installed.
    if not exist "OllamaSetup.exe" (
        echo 📥 Downloading Ollama for Windows...
        :: Utilisation de PowerShell pour un téléchargement plus robuste
        powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
    )
    
    echo 📦 Running installer... 
    echo ⚠️  IMPORTANT: Please finish the installation window, THEN CLOSE THIS BLACK TERMINAL AND RESTART IT.
    start /wait OllamaSetup.exe
    del OllamaSetup.exe
    pause
    exit
)

:: 2. ENSURE OLLAMA IS RUNNING
echo 🔄 Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 🚀 Starting Ollama background service...
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    timeout /t 5 /nobreak >nul
)

:: 3. DOWNLOAD THE AI MODEL
set "MODEL_NAME=llama3.1"
echo 🧠 Checking for model '%MODEL_NAME%'...
:: On vérifie si le modèle existe sans faire planter le script
ollama list | findstr /i "%MODEL_NAME%" >nul
if %ERRORLEVEL% neq 0 (
    echo 📥 Downloading the AI brain...
    ollama pull %MODEL_NAME%
)

:: 4. PYTHON ENVIRONMENT SETUP
if not exist venv (
    echo 📦 Setting up Python environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: 5. RUN THE WEB APP
echo.
echo ==========================================
echo 🌐 Opening Root AI in your browser...
echo ==========================================
python -m streamlit run main.py

pause