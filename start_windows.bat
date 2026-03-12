@echo off
chcp 65001 >nul
title Root AI - Debug Mode
cls

echo ==========================================
echo 🚀 Initializing Root AI...
echo ==========================================
echo.

cd /d "%~dp0"

:CHECK_PYTHON
echo [1/5] Checking Python...
py --version >nul 2>&1
if errorlevel 1 goto ERR_PYTHON
echo ✅ Python found.
echo.

:CHECK_OLLAMA_CMD
echo [2/5] Checking Ollama installation...
where ollama >nul 2>nul
if errorlevel 1 goto ERR_OLLAMA
echo ✅ Ollama command found.
echo.

:CHECK_OLLAMA_SERVICE
echo [3/5] Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>nul
if errorlevel 1 goto START_SERVICE
echo ✅ Ollama service is running.
echo.
goto CHECK_MODEL

:START_SERVICE
echo 🔄 Starting Ollama background service...
start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
echo ⏳ Waiting 5 seconds...
timeout /t 5 >nul
goto CHECK_MODEL

:CHECK_MODEL
echo [4/5] Checking AI Model...
set "MODEL_NAME=llama3.1"
ollama list > temp.txt 2>&1
findstr /i "%MODEL_NAME%" temp.txt >nul
if errorlevel 1 goto PULL_MODEL
del temp.txt
echo ✅ Model is ready.
echo.
goto SETUP_VENV

:PULL_MODEL
echo 📥 Downloading AI brain (4.7GB). Please wait...
if exist temp.txt del temp.txt
ollama pull %MODEL_NAME%
goto SETUP_VENV

:SETUP_VENV
echo [5/5] Setting up environment...
if not exist venv python -m venv venv
call venv\Scripts\activate.bat
echo ⏳ Installing libraries...
pip install -q -r requirements.txt
echo ✅ Environment ready.
echo.

echo ==========================================
echo 🎉 SUCCESS! Root AI is starting...
echo ==========================================
python -m streamlit run main.py
pause
exit

:: --- SECTIONS D'ERREURS (GOTO TARGETS) ---

:ERR_PYTHON
echo ❌ ERREUR : Python est absent.
where winget >nul 2>nul
if errorlevel 1 (
    echo ⚠️ winget n'est pas installé. Installez Python manuellement : https://www.python.org/downloads/
    echo ⚠️ COCHEZ BIEN "Add Python to PATH".
    pause
    exit
)

echo 🔄 Installation automatique de Python via winget...
winget install -e --id Python.Python.3 --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo ❌ Échec de l'installation automatique de Python. Merci d'installer manuellement : https://www.python.org/downloads/
    pause
    exit
)

echo ✅ Python installé. Relancez le script.
pause
exit

:ERR_OLLAMA
echo ❌ ERREUR : Ollama n'est pas installe.
echo Telechargement en cours...
curl.exe -L -o "OllamaSetup.exe" "https://ollama.com/download/OllamaSetup.exe"
start /wait OllamaSetup.exe
del OllamaSetup.exe
echo ✅ Installe fini. FERMEZ CETTE FENETRE et relancez.
pause
exit