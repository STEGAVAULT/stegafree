#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════
#  STEGA VAULT — Setup Dipendenze
#  Compatibile con: Linux (Debian/Ubuntu/Kali/Arch) e macOS
# ══════════════════════════════════════════════════════════════

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

ok()    { echo -e "  ${GREEN}[OK]${RESET}  $1"; }
err()   { echo -e "  ${RED}[ERRORE]${RESET}  $1"; }
info()  { echo -e "  ${CYAN}[...]${RESET}  $1"; }
warn()  { echo -e "  ${YELLOW}[ATTENZIONE]${RESET}  $1"; }

echo ""
echo -e "${BOLD}  ╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}  ║        STEGA VAULT  —  Setup Dipendenze          ║${RESET}"
echo -e "${BOLD}  ║              Base Edition  v1.0.0                ║${RESET}"
echo -e "${BOLD}  ╚══════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Rileva sistema operativo
OS="$(uname -s)"
case "$OS" in
    Linux*)   PLATFORM="Linux" ;;
    Darwin*)  PLATFORM="macOS" ;;
    *)        PLATFORM="Unknown" ;;
esac
ok "Sistema rilevato: $PLATFORM"
echo ""

# ── Controlla Python 3
info "[1/4]  Controllo installazione Python 3..."

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Verifica che sia Python 3 e non Python 2
    PY_MAJOR=$(python -c "import sys; print(sys.version_info.major)" 2>/dev/null)
    if [ "$PY_MAJOR" = "3" ]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    err "Python 3 non trovato sul tuo sistema."
    echo ""
    if [ "$PLATFORM" = "Linux" ]; then
        warn "Installa Python 3 con uno di questi comandi:"
        echo ""
        echo "    Ubuntu / Debian / Kali:"
        echo "      sudo apt update && sudo apt install python3 python3-pip -y"
        echo ""
        echo "    Arch / Manjaro:"
        echo "      sudo pacman -S python python-pip"
        echo ""
        echo "    Fedora / RHEL:"
        echo "      sudo dnf install python3 python3-pip"
    elif [ "$PLATFORM" = "macOS" ]; then
        warn "Installa Python 3 da: https://www.python.org/downloads/"
        warn "Oppure con Homebrew:  brew install python3"
    fi
    echo ""
    exit 1
fi

PYVER=$($PYTHON_CMD --version 2>&1)
ok "$PYVER trovato  (comando: $PYTHON_CMD)"

# Controlla versione minima 3.9
PY_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
PY_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]; }; then
    err "Stega Vault richiede Python 3.9 o superiore."
    err "Versione trovata: $PYVER"
    exit 1
fi
echo ""

# ── Controlla / installa pip
info "[2/4]  Controllo pip..."

PIP_CMD=""
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
elif command -v pip &>/dev/null; then
    PIP_CMD="pip"
fi

if [ -z "$PIP_CMD" ]; then
    warn "pip non trovato. Provo a installarlo..."
    $PYTHON_CMD -m ensurepip --upgrade 2>/dev/null
    if command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
        ok "pip installato con successo."
    else
        err "Impossibile installare pip automaticamente."
        echo ""
        if [ "$PLATFORM" = "Linux" ]; then
            echo "  Prova manualmente:"
            echo "    sudo apt install python3-pip    (Debian/Ubuntu/Kali)"
            echo "    sudo pacman -S python-pip       (Arch)"
        fi
        exit 1
    fi
else
    ok "pip disponibile  (comando: $PIP_CMD)"
fi
echo ""

# ── Aggiorna pip
info "[3/4]  Aggiornamento pip..."
$PYTHON_CMD -m pip install --upgrade pip --quiet 2>/dev/null
ok "pip aggiornato."
echo ""

# ── Installa dipendenze
info "[4/4]  Installazione dipendenze Stega Vault..."
echo ""

# customtkinter
info "Installazione customtkinter..."
if $PIP_CMD install customtkinter --quiet 2>/dev/null || \
   $PIP_CMD install customtkinter --break-system-packages --quiet 2>/dev/null; then
    ok "customtkinter installato."
else
    err "Impossibile installare customtkinter."
    err "Controlla la connessione internet e riprova."
    exit 1
fi

# pillow
info "Installazione pillow..."
if $PIP_CMD install pillow --quiet 2>/dev/null || \
   $PIP_CMD install pillow --break-system-packages --quiet 2>/dev/null; then
    ok "pillow installato."
else
    err "Impossibile installare pillow."
    err "Controlla la connessione internet e riprova."
    exit 1
fi
echo ""

# ── Verifica tkinter (richiesto da customtkinter, non installabile via pip)
info "Controllo tkinter (interfaccia grafica)..."
if ! $PYTHON_CMD -c "import tkinter" &>/dev/null; then
    warn "tkinter non trovato! E' necessario per l'interfaccia grafica."
    echo ""
    if [ "$PLATFORM" = "Linux" ]; then
        echo "  Installalo con:"
        echo "    sudo apt install python3-tk    (Debian/Ubuntu/Kali)"
        echo "    sudo pacman -S tk              (Arch)"
        echo "    sudo dnf install python3-tkinter  (Fedora)"
        echo ""
        read -p "  Vuoi che provi a installarlo automaticamente? [s/N] " choice
        if [[ "$choice" =~ ^[Ss]$ ]]; then
            if command -v apt &>/dev/null; then
                sudo apt install python3-tk -y
            elif command -v pacman &>/dev/null; then
                sudo pacman -S tk --noconfirm
            elif command -v dnf &>/dev/null; then
                sudo dnf install python3-tkinter -y
            else
                err "Package manager non riconosciuto. Installa python3-tk manualmente."
                exit 1
            fi
        else
            err "Installa python3-tk manualmente e riavvia questo script."
            exit 1
        fi
    elif [ "$PLATFORM" = "macOS" ]; then
        warn "Installa Python da python.org (include tkinter) oppure:"
        warn "  brew install python-tk"
    fi
fi
ok "tkinter disponibile."
echo ""

# ── Verifica finale importando tutti i moduli
info "Verifica finale importazione moduli..."
if $PYTHON_CMD -c "import customtkinter, PIL, tkinter" &>/dev/null; then
    ok "Tutti i moduli importati correttamente."
else
    err "Qualcosa e' andato storto durante la verifica."
    err "Prova a installare manualmente:"
    echo ""
    echo "    $PIP_CMD install customtkinter pillow"
    exit 1
fi
echo ""

# ── Rendi eseguibile stega_vault.py se presente
if [ -f "stega_vault.py" ]; then
    chmod +x stega_vault.py
    ok "stega_vault.py reso eseguibile."
fi

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║   Installazione completata con successo!  ✔      ║"
echo "  ║                                                  ║"
echo "  ║   Per avviare Stega Vault:                       ║"
echo "  ║     $PYTHON_CMD stega_vault.py                   ║"
echo "  ║                                                  ║"
echo "  ║   Oppure (se nella stessa cartella):             ║"
echo "  ║     ./stega_vault.py                             ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo -e "${RESET}"
