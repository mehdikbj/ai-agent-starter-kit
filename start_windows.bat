@echo off
chcp 65001 >nul
title Root AI - System Check
cls

echo ==========================================
echo 🚀 Initializing Root AI...
echo ==========================================
echo.

cd /d "%~dp0"

:: --- 1. CHECK PYTHON ---
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ ERREUR : Python n'est pas détecté sur votre système.
    echo.
    echo Pour faire fonctionner Root AI, vous devez installer Python :
    echo 1. Téléchargez-le ici : https://www.python.org/downloads/
    echo 2. ⚠️ TRÈS IMPORTANT : Cochez la case "Add Python to PATH" 
    echo    au début de l'installation.
    echo.
    echo Une fois installé, fermez ce terminal et relancez ce script.
    echo.
    pause
    exit
)

:: --- 2. CHECK OLLAMA ---
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚙️ Ollama is not installed.
    if not exist "OllamaSetup.exe" (
        echo 📥 Downloading Ollama for Windows...
        powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
    )
    echo 📦 Running installer...
    echo ✅ Une fois Ollama installé, fermez ce terminal et relancez le script.
    start /wait OllamaSetup.exe
    del OllamaSetup.exe
    pause
    exit
)

:: --- 3. SERVICES & VENV ---
echo 🔄 Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% neq 0 (
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    timeout /t 5 /nobreak >nul
)

set "MODEL_NAME=llama3.1"
echo 🧠 Checking model '%MODEL_NAME%'...
ollama list | findstr /i "%MODEL_NAME%" >nul
if %ERRORLEVEL% neq 0 (
    echo 📥 Downloading AI brain (4.7GB)...
    ollama pull %MODEL_NAME%
)

if not exist venv (
    echo 📦 Creating Python Virtual Environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo ⏳ Syncing dependencies (Streamlit, PydanticAI)...
pip install -q -r requirements.txt

echo.
echo ==========================================
echo 🌐 Root AI is ready! Opening your browser...
echo ==========================================
python -m streamlit run main.py

pause