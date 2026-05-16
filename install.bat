@echo off
chcp 65001 >nul
title Stega Vault — Installazione Dipendenze

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║        STEGA VAULT  —  Setup Dipendenze          ║
echo  ║              Base Edition  v1.0.0                ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: ── Controlla che Python sia installato
echo  [1/4]  Controllo installazione Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERRORE] Python non trovato sul tuo sistema.
    echo.
    echo  Scaricalo gratuitamente da:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANTE: durante l'installazione spunta
    echo  la casella "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  [OK] %PYVER% trovato.
echo.

:: ── Controlla che pip sia disponibile
echo  [2/4]  Controllo pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERRORE] pip non trovato. Provo a installarlo...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo  [ERRORE] Impossibile installare pip. Riinstalla Python.
        pause
        exit /b 1
    )
)
echo  [OK] pip disponibile.
echo.

:: ── Aggiorna pip
echo  [3/4]  Aggiornamento pip...
python -m pip install --upgrade pip --quiet
echo  [OK] pip aggiornato.
echo.

:: ── Installa le dipendenze
echo  [4/4]  Installazione dipendenze Stega Vault...
echo.
echo  Installazione customtkinter...
pip install customtkinter --quiet
if %errorlevel% neq 0 (
    echo  [ERRORE] Impossibile installare customtkinter.
    echo  Controlla la tua connessione internet e riprova.
    pause
    exit /b 1
)
echo  [OK] customtkinter installato.

echo  Installazione pillow...
pip install pillow --quiet
if %errorlevel% neq 0 (
    echo  [ERRORE] Impossibile installare pillow.
    echo  Controlla la tua connessione internet e riprova.
    pause
    exit /b 1
)
echo  [OK] pillow installato.
echo.

:: ── Verifica finale importando i moduli
echo  Verifica installazione...
python -c "import customtkinter, PIL; print('  [OK] Tutti i moduli funzionanti.')"
if %errorlevel% neq 0 (
    echo  [ERRORE] Qualcosa e' andato storto. Riprova o installa manualmente.
    pause
    exit /b 1
)
echo.

echo  ╔══════════════════════════════════════════════════╗
echo  ║   Installazione completata con successo!         ║
echo  ║                                                  ║
echo  ║   Per avviare Stega Vault:                       ║
echo  ║     python stega_vault.py                        ║
echo  ║                                                  ║
echo  ║   Oppure fai doppio clic su stega_vault.py       ║
echo  ╚══════════════════════════════════════════════════╝
echo.
pause
