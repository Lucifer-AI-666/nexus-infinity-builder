@echo off
REM ========================================
REM NEXUS INFINITY REAL - AUTO SETUP & START
REM ========================================
REM Questo script prepara e avvia il sistema completo

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║         NEXUS INFINITY REAL - SISTEMA AVVIO           ║
echo ║    Sistema Operativo per Agenti AI con Groq           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM ========================================
REM 1. VERIFICA PYTHON
REM ========================================
echo [1/4] Verifica Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRORE: Python non trovato!
    echo.
    echo Scarica Python da: https://www.python.org/downloads/
    echo Assicurati di selezionare "Add Python to PATH" durante l'installazione
    echo.
    pause
    exit /b 1
)
echo ✅ Python trovato

REM ========================================
REM 2. CREA AMBIENTE VIRTUALE
REM ========================================
echo.
echo [2/4] Setup ambiente Python...
if not exist "venv" (
    echo 🔧 Creazione ambiente virtuale...
    python -m venv venv
    echo ✅ Ambiente virtuale creato
) else (
    echo ✅ Ambiente virtuale già presente
)

REM ========================================
REM 3. ATTIVA VENV E INSTALLA DIPENDENZE
REM ========================================
echo.
echo [3/4] Installazione dipendenze...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip -q

REM Installa dipendenze
if exist "requirements.txt" (
    pip install -r requirements.txt -q
    echo ✅ Dipendenze installate
) else (
    echo ⚠️  File requirements.txt non trovato
)

REM ========================================
REM 4. CONFIGURAZIONE .ENV
REM ========================================
echo.
echo [4/4] Configurazione ambiente...

if not exist ".env" (
    echo 🔑 Creazione file .env...
    (
        echo # Groq API Configuration
        echo GROQ_API_KEY=your_groq_api_key_here
        echo.
        echo # API Server Configuration
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo API_DEBUG=false
        echo.
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///nexus.db
        echo.
        echo # Security
        echo SECURITY_LEVEL=high
        echo ENABLE_AUDIT_LOG=true
    ) > .env
    echo ✅ File .env creato
    echo.
    echo ⚠️  IMPORTANTE: Modifica il file .env e aggiungi la tua chiave Groq!
    echo   GROQ_API_KEY=your_groq_api_key_here
    echo.
) else (
    echo ✅ File .env già presente
)

REM ========================================
REM AVVIO DEL SISTEMA
REM ========================================
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              NEXUS INFINITY READY TO START             ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Scegli la modalità di avvio:
echo.
echo   1) CLI Interattiva (main.py)
echo   2) API Server (api_server.py - http://localhost:8000)
echo   3) Entrambi (CLI + API in parallelo)
echo   4) Esci
echo.

set /p choice="Seleziona (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Avvio CLI Interattiva...
    echo.
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Avvio API Server...
    echo   📍 Accedi a: http://localhost:8000/docs
    echo.
    python api_server.py
) else if "%choice%"=="3" (
    echo.
    echo 🚀 Avvio CLI + API in parallelo...
    echo   📍 API disponibile su: http://localhost:8000/docs
    echo.
    start "Nexus CLI" python main.py
    timeout /t 2 /nobreak
    start "Nexus API" python api_server.py
    echo.
    echo ✅ Entrambi i servizi avviati!
    echo.
    pause
) else (
    echo.
    echo Uscita.
    pause
    exit /b 0
)

REM Mantieni la finestra aperta se c'è un errore
if errorlevel 1 (
    echo.
    echo ❌ Errore durante l'esecuzione
    pause
    exit /b 1
)

pause
