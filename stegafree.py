"""
╔══════════════════════════════════════════════════════════════╗
║              STEGA VAULT  –  Base / Free Edition             ║
║         Steganografia LSB per immagini PNG  |  Python        ║
╚══════════════════════════════════════════════════════════════╝

Dipendenze:
    pip install customtkinter pillow

Per compilare in .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "StegaVault" stega_vault.py
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from PIL import Image
import threading
import itertools
import pathlib
import random
import sys
import os

# ─────────────────────────────────────────────────────────────
#  COSTANTI GLOBALI
# ─────────────────────────────────────────────────────────────
APP_TITLE        = "Stega Vault  |  Base Edition"
APP_VERSION      = "v1.0.0"
APP_GEOMETRY     = "920x680"
MAX_FILE_SIZE_MB = 2
WALLET_ADDRESS   = "BhCKExQLYdYhHFXF9kojaYFmS3gVbQxYEYyi66CRg2tJ"   # ← sostituisci con il tuo

ACCENT_GREEN     = "#00FF9C"
ACCENT_CYAN      = "#00D4FF"
ACCENT_RED       = "#FF4D6D"
ACCENT_YELLOW    = "#FFD60A"
BG_DARK          = "#0D0D0D"
BG_PANEL         = "#111827"
BG_WIDGET        = "#1A2332"
BORDER_COLOR     = "#1E3A5F"
TEXT_DIM         = "#8899AA"

SECURITY_TIPS = [
    "💡  Le app di messaggistica (WhatsApp, Telegram, ecc.) comprimono le immagini "
    "distruggendo i dati LSB. Invia sempre il file come DOCUMENTO.",
    "💡  Usa esclusivamente il formato PNG: JPEG e WebP sono con perdita di dati "
    "e corrompono il payload steganografico.",
    "💡  Non condividere l'immagine originale e quella codificata sullo stesso canale.",
    "💡  Abilita BitLocker o VeraCrypt per cifrare il disco su cui salvi le immagini.",
    "💡  Aggiorna Windows regolarmente: molte vulnerabilità sfruttate attivamente "
    "sono già patchate nelle versioni recenti.",
    "💡  Usa password manager (Bitwarden, KeePass) e mai password riutilizzate.",
    "💡  Le immagini caricate sui social vengono ricompresse automaticamente: "
    "non usare Facebook/Instagram per trasmettere file steganografici.",
    "💡  Attiva l'autenticazione a due fattori (2FA) su tutti gli account critici.",
    "💡  Considera di cifrare il testo con AES prima di nasconderlo: "
    "la steganografia da sola non è cifratura.",
    "💡  Esegui backup regolari su supporti offline (regola 3-2-1).",
    "💡  Diffida degli allegati e-mail anche se sembrano provenire da mittenti noti.",
    "💡  Un'immagine PNG di 1920×1080 può contenere circa 700 KB di testo nascosto.",
]


# ─────────────────────────────────────────────────────────────
#  MOTORE STEGANOGRAFICO LSB
# ─────────────────────────────────────────────────────────────
DELIMITER = "<<STEGAVAULT_END>>"

def _text_to_bits(text: str) -> str:
    encoded = text.encode("utf-8")
    return "".join(format(byte, "08b") for byte in encoded)

def _bits_to_text(bits: str) -> str:
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    byte_list = []
    for c in chars:
        if len(c) < 8:
            break
        byte_list.append(int(c, 2))
    return bytes(byte_list).decode("utf-8", errors="replace")

def encode_lsb(image_path: pathlib.Path, secret_text: str,
               output_path: pathlib.Path) -> None:
    """Nasconde secret_text nell'immagine PNG tramite LSB."""
    img = Image.open(image_path).convert("RGBA")
    pixels = list(img.getdata())

    payload = secret_text + DELIMITER
    bits    = _text_to_bits(payload)
    total   = len(bits)

    # Verifica capienza
    if total > len(pixels) * 3:
        raise ValueError(
            f"Il testo è troppo lungo per questa immagine "
            f"({total} bit richiesti, {len(pixels)*3} disponibili)."
        )

    bit_iter = itertools.chain(iter(bits), itertools.repeat(None))
    new_pixels = []
    for r, g, b, a in pixels:
        channels = [r, g, b]
        new_ch   = []
        for ch in channels:
            bit = next(bit_iter)
            if bit is not None:
                ch = (ch & ~1) | int(bit)
            new_ch.append(ch)
        new_pixels.append(tuple(new_ch) + (a,))

    out_img = Image.new("RGBA", img.size)
    out_img.putdata(new_pixels)
    out_img.save(str(output_path), format="PNG")

def decode_lsb(image_path: pathlib.Path) -> str:
    """Estrae il testo nascosto dall'immagine PNG."""
    img    = Image.open(image_path).convert("RGBA")
    pixels = list(img.getdata())

    bits = []
    for r, g, b, a in pixels:
        bits += [str(r & 1), str(g & 1), str(b & 1)]

    bit_str  = "".join(bits)
    raw_text = _bits_to_text(bit_str)

    if DELIMITER in raw_text:
        return raw_text.split(DELIMITER)[0]
    raise ValueError(
        "Nessun payload trovato.\n"
        "L'immagine non sembra essere stata codificata con Stega Vault, "
        "oppure è stata compressa/modificata."
    )


# ─────────────────────────────────────────────────────────────
#  WIDGET PERSONALIZZATI
# ─────────────────────────────────────────────────────────────
def GlowButton(master, glow_color=ACCENT_GREEN, **kwargs):
    """Pulsante con effetto glow (factory function, evita conflitti con CTkButton)."""
    kwargs.setdefault("corner_radius", 8)
    kwargs.setdefault("font", ctk.CTkFont("Consolas", 13, weight="bold"))
    _border = kwargs.get("border_color", BORDER_COLOR)
    btn = ctk.CTkButton(master, **kwargs)
    btn.bind("<Enter>", lambda e: btn.configure(border_color=glow_color, border_width=1))
    btn.bind("<Leave>", lambda e: btn.configure(border_color=_border, border_width=1))
    return btn


class WalletBadge(ctk.CTkFrame):
    """Badge wallet con pulsante copia integrato."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_WIDGET, corner_radius=6,
                         border_color=BORDER_COLOR, border_width=1, **kwargs)

        ctk.CTkLabel(self, text="₿  Donazioni / Support",
                     font=ctk.CTkFont("Consolas", 10, weight="bold"),
                     text_color=ACCENT_YELLOW).pack(padx=10, pady=(8, 2))

        # Riga indirizzo + pulsante copia
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=(0, 8))

        addr_lbl = ctk.CTkLabel(row,
                     text=WALLET_ADDRESS,
                     font=ctk.CTkFont("Consolas", 8),
                     text_color=TEXT_DIM, wraplength=150, justify="left")
        addr_lbl.pack(side="left", padx=(4, 6))

        self._copy_btn = ctk.CTkButton(
            row, text="📋 Copia", width=70, height=26,
            font=ctk.CTkFont("Consolas", 9, weight="bold"),
            fg_color="#1A2B1A", hover_color="#223322",
            text_color=ACCENT_GREEN,
            border_color=ACCENT_GREEN, border_width=1,
            corner_radius=6,
            command=self._copy_wallet,
        )
        self._copy_btn.pack(side="right", padx=4)

    def _copy_wallet(self):
        self.clipboard_clear()
        self.clipboard_append(WALLET_ADDRESS)
        self._copy_btn.configure(text="✔ Copiato!", text_color=ACCENT_YELLOW,
                                  border_color=ACCENT_YELLOW)
        self.after(2000, lambda: self._copy_btn.configure(
            text="📋 Copia", text_color=ACCENT_GREEN, border_color=ACCENT_GREEN))


# ─────────────────────────────────────────────────────────────
#  SCHERMATA 1 – DISCLAIMER LEGALE
# ─────────────────────────────────────────────────────────────
DISCLAIMER_TEXT = """\
⬡  STEGA VAULT  –  Disclaimer Legale e Condizioni d'Uso
═══════════════════════════════════════════════════════════════════

Il presente software ("Stega Vault") è fornito ESCLUSIVAMENTE a scopo
educativo, di ricerca e di uso lecito nell'ambito della sicurezza
informatica e della tutela della privacy personale.

1.  LIMITAZIONE DI RESPONSABILITÀ
    Lo sviluppatore di Stega Vault declina espressamente qualsiasi
    responsabilità civile, penale o amministrativa per danni diretti
    o indiretti derivanti dall'utilizzo di questo software.

2.  USO VIETATO
    È severamente vietato utilizzare questo software per:
    • Attività illegali, fraudolente o criminali;
    • Occultamento di materiale illecito (CSAM, dati rubati, ecc.);
    • Elusione di sistemi di sorveglianza o DRM;
    • Qualsiasi violazione delle leggi locali, nazionali o internazionali.

3.  RESPONSABILITÀ DELL'UTENTE
    L'utente è l'unico ed esclusivo responsabile dell'uso che fa di
    questo strumento. Cliccando "Accetto e Continua" l'utente dichiara
    di aver letto il presente avviso, di comprenderlo e di accettarne
    integralmente i termini.

4.  NESSUNA GARANZIA
    Il software è fornito "così com'è" (AS IS) senza garanzie di alcun
    tipo, espresse o implicite, incluse quelle di commerciabilità e
    idoneità a scopi particolari.

5.  PROPRIETÀ INTELLETTUALE
    Il codice sorgente è soggetto a copyright. Qualsiasi ridistribuzione
    non autorizzata è vietata.

───────────────────────────────────────────────────────────────────
Se non accetti questi termini, chiudi immediatamente l'applicazione.
───────────────────────────────────────────────────────────────────


★  PERCHÉ SCEGLIERE STEGA VAULT
═══════════════════════════════════════════════════════════════════

Il mercato offre diversi tool steganografici. Ecco perché Stega Vault
si distingue concretamente dalla concorrenza:

┌─────────────────────────────────────────────────────────────────┐
│  CONFRONTO CON GLI STRUMENTI PIÙ DIFFUSI                        │
├───────────────────────┬─────────────────┬───────────────────────┤
│  Strumento            │  Limite         │  Stega Vault invece…  │
├───────────────────────┼─────────────────┼───────────────────────┤
│  OpenStego            │  UI anni '90,   │  Interfaccia moderna  │
│                       │  Java richiesto │  nativa, zero JVM     │
├───────────────────────┼─────────────────┼───────────────────────┤
│  SilentEye            │  Abbandonato    │  Mantenuto e          │
│                       │  dal 2012       │  aggiornato           │
├───────────────────────┼─────────────────┼───────────────────────┤
│  Steghide             │  Solo CLI,      │  GUI completa,        │
│                       │  nessuna GUI    │  adatta a tutti       │
├───────────────────────┼─────────────────┼───────────────────────┤
│  Online tools         │  Il tuo testo   │  100% offline,        │
│  (web-based)          │  passa su server│  nessun dato in rete  │
├───────────────────────┼─────────────────┼───────────────────────┤
│  StegSolve            │  Solo analisi,  │  Encode + Decode +    │
│                       │  non crea file  │  Stats in un tool     │
└───────────────────────┴─────────────────┴───────────────────────┘

  ✔  ZERO DIPENDENZE ESTERNE  –  Funziona offline, nessuna connessione
     a internet richiesta. I tuoi dati non lasciano mai il tuo PC.

  ✔  PORTABILE  –  Un singolo file .py o .exe. Nessun installer,
     nessun registro di sistema modificato.

  ✔  OPEN & TRASPARENTE  –  Il codice sorgente è leggibile e
     verificabile. Sai esattamente cosa fa il software.

  ✔  DELIMITATORE PROPRIETARIO  –  Stega Vault usa un marker interno
     univoco (<<STEGAVAULT_END>>) per un'estrazione affidabile anche
     su immagini con spazio residuo non utilizzato.

  ✔  STATISTICHE DI SESSIONE  –  Tieni traccia di quante operazioni
     hai eseguito e quanti dati hai protetto, in tempo reale.

  ✔  CROSS-PLATFORM  –  Gira su Windows, Linux e macOS senza
     modifiche al codice.

  ✔  CONSIGLI DI SICUREZZA INTEGRATI  –  Suggerimenti rotativi su
     best practice OpSec direttamente nell'interfaccia.

───────────────────────────────────────────────────────────────────
Se non accetti questi termini, chiudi immediatamente l'applicazione.
───────────────────────────────────────────────────────────────────
"""

class DisclaimerScreen(ctk.CTkFrame):
    def __init__(self, master, on_accept, **kwargs):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0, **kwargs)
        self._on_accept = on_accept
        self._build()

    def _build(self):
        # ── Logo testuale
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(28, 0))

        ctk.CTkLabel(header,
                     text="⬡  STEGA VAULT",
                     font=ctk.CTkFont("Consolas", 28, weight="bold"),
                     text_color=ACCENT_GREEN).pack(side="left")
        ctk.CTkLabel(header,
                     text=f"Base Edition  {APP_VERSION}",
                     font=ctk.CTkFont("Consolas", 12),
                     text_color=TEXT_DIM).pack(side="left", padx=(12, 0), pady=(8, 0))

        # ── Separatore
        sep = ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR)
        sep.pack(fill="x", padx=40, pady=(14, 18))

        # ── Textbox con il disclaimer
        txt_frame = ctk.CTkFrame(self, fg_color=BG_PANEL,
                                  corner_radius=10,
                                  border_color=BORDER_COLOR, border_width=1)
        txt_frame.pack(fill="both", expand=True, padx=40, pady=(0, 0))

        textbox = ctk.CTkTextbox(
            txt_frame,
            font=ctk.CTkFont("Consolas", 12),
            fg_color="transparent",
            text_color="#C8D8E8",
            wrap="word",
            activate_scrollbars=True,
        )
        textbox.pack(fill="both", expand=True, padx=16, pady=16)
        textbox.insert("1.0", DISCLAIMER_TEXT)
        textbox.configure(state="disabled")

        # ── Wallet per donazioni
        sep2 = ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR)
        sep2.pack(fill="x", padx=40, pady=(18, 12))

        wallet_frame = ctk.CTkFrame(self, fg_color="transparent")
        wallet_frame.pack(fill="x", padx=40, pady=(0, 8))
        ctk.CTkLabel(wallet_frame,
                     text="₿  Supporta il progetto  –  Wallet SOL:",
                     font=ctk.CTkFont("Consolas", 11, weight="bold"),
                     text_color=ACCENT_YELLOW).pack(side="left")
        ctk.CTkLabel(wallet_frame,
                     text=f"  {WALLET_ADDRESS}",
                     font=ctk.CTkFont("Consolas", 11),
                     text_color=TEXT_DIM).pack(side="left")

        # ── Pulsante Accetta
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=(10, 28))

        GlowButton(
            btn_row,
            text="✔   Accetto e Continua",
            glow_color=ACCENT_GREEN,
            command=self._on_accept,
            width=280,
            height=46,
            fg_color="#003322",
            hover_color="#004433",
            text_color=ACCENT_GREEN,
            border_color=ACCENT_GREEN,
            border_width=1,
            font=ctk.CTkFont("Consolas", 14, weight="bold"),
        ).pack(side="left", padx=8)

        GlowButton(
            btn_row,
            text="✖   Rifiuta ed Esci",
            glow_color=ACCENT_RED,
            command=self._quit_app,
            width=200,
            height=46,
            fg_color="#220011",
            hover_color="#330011",
            text_color=ACCENT_RED,
            border_color=ACCENT_RED,
            border_width=1,
            font=ctk.CTkFont("Consolas", 14, weight="bold"),
        ).pack(side="left", padx=8)

    def _quit_app(self):
        self.master.destroy()


# ─────────────────────────────────────────────────────────────
#  SCHERMATA 2 – APPLICAZIONE PRINCIPALE
# ─────────────────────────────────────────────────────────────
class MainAppScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0, **kwargs)
        self._tip_cycle   = itertools.cycle(random.sample(SECURITY_TIPS, len(SECURITY_TIPS)))
        self._tip_job     = None
        self._encode_img  = None
        self._decode_img  = None
        # ── Statistiche di sessione
        self._stat_encode_ok  = 0
        self._stat_decode_ok  = 0
        self._stat_encode_err = 0
        self._stat_decode_err = 0
        self._stat_bytes_hidden   = 0
        self._stat_bytes_extracted = 0
        self._build()
        self._start_tip_rotation()

    # ── Layout principale
    def _build(self):
        # TOP BAR
        topbar = ctk.CTkFrame(self, fg_color=BG_PANEL,
                               border_color=BORDER_COLOR, border_width=1,
                               corner_radius=0, height=52)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar,
                     text="⬡  STEGA VAULT",
                     font=ctk.CTkFont("Consolas", 20, weight="bold"),
                     text_color=ACCENT_GREEN).pack(side="left", padx=20)
        ctk.CTkLabel(topbar,
                     text=f"Base Edition  {APP_VERSION}",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=TEXT_DIM).pack(side="left", pady=(8, 0))

        # CONTENT AREA  (sidebar + pannello centrale)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=0, pady=0)

        # Sidebar
        sidebar = ctk.CTkFrame(content, fg_color=BG_PANEL, width=220,
                                border_color=BORDER_COLOR, border_width=1,
                                corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Pannello centrale con tab
        center = ctk.CTkFrame(content, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True, padx=16, pady=16)
        self._build_center(center)

    # ── SIDEBAR
    def _build_sidebar(self, parent):
        ctk.CTkLabel(parent, text="STEGA VAULT",
                     font=ctk.CTkFont("Consolas", 13, weight="bold"),
                     text_color=ACCENT_GREEN).pack(pady=(20, 2), padx=16, anchor="w")
        ctk.CTkLabel(parent, text="Base Edition",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=TEXT_DIM).pack(padx=16, anchor="w")

        sep = ctk.CTkFrame(parent, height=1, fg_color=BORDER_COLOR)
        sep.pack(fill="x", padx=16, pady=16)

        # Tip box
        ctk.CTkLabel(parent, text="SECURITY TIPS",
                     font=ctk.CTkFont("Consolas", 10, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=16, anchor="w")

        tip_container = ctk.CTkFrame(parent, fg_color=BG_WIDGET,
                                      corner_radius=8,
                                      border_color=BORDER_COLOR, border_width=1)
        tip_container.pack(fill="x", padx=10, pady=(6, 0))

        self._tip_label = ctk.CTkLabel(
            tip_container,
            text="",
            font=ctk.CTkFont("Consolas", 10),
            text_color="#9AABB8",
            wraplength=180,
            justify="left",
        )
        self._tip_label.pack(padx=10, pady=10)

        sep2 = ctk.CTkFrame(parent, height=1, fg_color=BORDER_COLOR)
        sep2.pack(fill="x", padx=16, pady=18)

        # Wallet badge
        WalletBadge(parent).pack(fill="x", padx=10, pady=(0, 16))

    # ── AREA CENTRALE
    def _build_center(self, parent):
        # Tab bar encode / decode
        tab_bar = ctk.CTkFrame(parent, fg_color=BG_WIDGET,
                                corner_radius=8, height=40)
        tab_bar.pack(fill="x", pady=(0, 10))
        tab_bar.pack_propagate(False)

        self._tab_enc_btn = ctk.CTkButton(
            tab_bar, text="🔒  ENCODE", width=160, height=34,
            font=ctk.CTkFont("Consolas", 12, weight="bold"),
            fg_color=ACCENT_GREEN, text_color="#000000",
            hover_color="#00CC7A", corner_radius=6,
            command=self._show_encode,
        )
        self._tab_enc_btn.pack(side="left", padx=(6, 4), pady=3)

        self._tab_dec_btn = ctk.CTkButton(
            tab_bar, text="🔓  DECODE", width=160, height=34,
            font=ctk.CTkFont("Consolas", 12, weight="bold"),
            fg_color=BG_PANEL, text_color=ACCENT_CYAN,
            hover_color="#1A2332", corner_radius=6,
            border_color=ACCENT_CYAN, border_width=1,
            command=self._show_decode,
        )
        self._tab_dec_btn.pack(side="left", padx=4, pady=3)

        self._tab_stat_btn = ctk.CTkButton(
            tab_bar, text="📊  STATS", width=140, height=34,
            font=ctk.CTkFont("Consolas", 12, weight="bold"),
            fg_color=BG_PANEL, text_color=ACCENT_YELLOW,
            hover_color="#1A2332", corner_radius=6,
            border_color=ACCENT_YELLOW, border_width=1,
            command=self._show_stats,
        )
        self._tab_stat_btn.pack(side="left", padx=4, pady=3)

        # Container card
        self._card_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._card_frame.pack(fill="both", expand=True)

        self._encode_frame = self._build_encode_panel(self._card_frame)
        self._decode_frame = self._build_decode_panel(self._card_frame)
        self._stats_frame  = self._build_stats_panel(self._card_frame)

        # Mostra encode per default
        self._show_encode()

    def _hide_all_panels(self):
        for f in (self._encode_frame, self._decode_frame, self._stats_frame):
            f.pack_forget()
        self._tab_enc_btn.configure(fg_color=BG_PANEL, text_color=ACCENT_GREEN)
        self._tab_dec_btn.configure(fg_color=BG_PANEL, text_color=ACCENT_CYAN)
        self._tab_stat_btn.configure(fg_color=BG_PANEL, text_color=ACCENT_YELLOW)

    def _show_encode(self):
        self._hide_all_panels()
        self._encode_frame.pack(fill="both", expand=True)
        self._tab_enc_btn.configure(fg_color=ACCENT_GREEN, text_color="#000000")

    def _show_decode(self):
        self._hide_all_panels()
        self._decode_frame.pack(fill="both", expand=True)
        self._tab_dec_btn.configure(fg_color=ACCENT_CYAN, text_color="#000000")

    def _show_stats(self):
        self._hide_all_panels()
        self._stats_frame.pack(fill="both", expand=True)
        self._tab_stat_btn.configure(fg_color=ACCENT_YELLOW, text_color="#000000")
        self._refresh_stats()

    # ────────────────── PANNELLO ENCODE ──────────────────
    def _build_encode_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=BG_PANEL,
                              corner_radius=12,
                              border_color=BORDER_COLOR, border_width=1)

        ctk.CTkLabel(frame,
                     text="🔒  ENCODE  –  Nascondi testo in un'immagine PNG",
                     font=ctk.CTkFont("Consolas", 15, weight="bold"),
                     text_color=ACCENT_GREEN).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(frame,
                     text="Seleziona un'immagine PNG di copertura, inserisci il testo segreto o carica un .txt, "
                          "poi salva il file codificato.",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=TEXT_DIM, wraplength=580, justify="left").pack(anchor="w", padx=24, pady=(0, 14))

        sep = ctk.CTkFrame(frame, height=1, fg_color=BORDER_COLOR)
        sep.pack(fill="x", padx=24, pady=(0, 14))

        # ── Selezione immagine
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(row1, text="Immagine PNG di copertura:",
                     font=ctk.CTkFont("Consolas", 11), text_color="#C8D8E8").pack(side="left")
        self._enc_img_label = ctk.CTkLabel(row1, text="  nessun file selezionato",
                                            font=ctk.CTkFont("Consolas", 10),
                                            text_color=TEXT_DIM)
        self._enc_img_label.pack(side="left", padx=8)
        GlowButton(row1, text="📁 Sfoglia", command=self._browse_encode_image,
                   width=100, height=32, fg_color=BG_WIDGET,
                   hover_color="#243040", text_color="#C8D8E8",
                   border_color=BORDER_COLOR).pack(side="right")

        # ── Testo segreto
        ctk.CTkLabel(frame, text="Testo segreto (digita oppure carica un .txt):",
                     font=ctk.CTkFont("Consolas", 11), text_color="#C8D8E8",
                     anchor="w").pack(fill="x", padx=24, pady=(0, 4))

        self._enc_textbox = ctk.CTkTextbox(frame, height=160,
                                            font=ctk.CTkFont("Consolas", 11),
                                            fg_color=BG_WIDGET,
                                            text_color="#E0F0FF",
                                            border_color=BORDER_COLOR, border_width=1,
                                            corner_radius=8)
        self._enc_textbox.pack(fill="x", padx=24, pady=(0, 8))
        self._enc_textbox.insert("1.0", "Inserisci qui il testo da nascondere…")
        self._enc_textbox.bind("<FocusIn>", self._clear_enc_placeholder)

        # ── Riga carica .txt + Encode
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=24, pady=(0, 14))
        GlowButton(row2, text="📄 Carica .txt",
                   command=self._load_txt_encode,
                   width=130, height=36, fg_color=BG_WIDGET,
                   hover_color="#243040", text_color="#C8D8E8",
                   border_color=BORDER_COLOR).pack(side="left", padx=(0, 8))

        GlowButton(row2, text="🔒  ENCODE  →  Salva PNG",
                   glow_color=ACCENT_GREEN,
                   command=self._run_encode,
                   width=230, height=36, fg_color="#003322",
                   hover_color="#004433", text_color=ACCENT_GREEN,
                   border_color=ACCENT_GREEN).pack(side="right")

        # ── Status
        self._enc_status = ctk.CTkLabel(frame, text="",
                                         font=ctk.CTkFont("Consolas", 11),
                                         text_color=ACCENT_GREEN)
        self._enc_status.pack(padx=24, pady=(0, 16), anchor="w")

        return frame

    # ────────────────── PANNELLO DECODE ──────────────────
    def _build_decode_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=BG_PANEL,
                              corner_radius=12,
                              border_color=BORDER_COLOR, border_width=1)

        ctk.CTkLabel(frame,
                     text="🔓  DECODE  –  Estrai testo nascosto da un PNG",
                     font=ctk.CTkFont("Consolas", 15, weight="bold"),
                     text_color=ACCENT_CYAN).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(frame,
                     text="Seleziona l'immagine PNG codificata con Stega Vault e il testo verrà estratto automaticamente.",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=TEXT_DIM, wraplength=580, justify="left").pack(anchor="w", padx=24, pady=(0, 14))

        sep = ctk.CTkFrame(frame, height=1, fg_color=BORDER_COLOR)
        sep.pack(fill="x", padx=24, pady=(0, 14))

        # ── Selezione immagine
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(row1, text="Immagine PNG codificata:",
                     font=ctk.CTkFont("Consolas", 11), text_color="#C8D8E8").pack(side="left")
        self._dec_img_label = ctk.CTkLabel(row1, text="  nessun file selezionato",
                                            font=ctk.CTkFont("Consolas", 10),
                                            text_color=TEXT_DIM)
        self._dec_img_label.pack(side="left", padx=8)
        GlowButton(row1, text="📁 Sfoglia", command=self._browse_decode_image,
                   width=100, height=32, fg_color=BG_WIDGET,
                   hover_color="#243040", text_color="#C8D8E8",
                   border_color=BORDER_COLOR).pack(side="right")

        # ── Pulsante Decode
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=24, pady=(4, 12))
        GlowButton(row2, text="🔓  DECODE  →  Estrai Testo",
                   glow_color=ACCENT_CYAN,
                   command=self._run_decode,
                   width=230, height=36, fg_color="#00222A",
                   hover_color="#003344", text_color=ACCENT_CYAN,
                   border_color=ACCENT_CYAN).pack(side="right")

        # ── Output
        ctk.CTkLabel(frame, text="Testo estratto:",
                     font=ctk.CTkFont("Consolas", 11), text_color="#C8D8E8",
                     anchor="w").pack(fill="x", padx=24, pady=(0, 4))

        self._dec_textbox = ctk.CTkTextbox(frame, height=200,
                                            font=ctk.CTkFont("Consolas", 11),
                                            fg_color=BG_WIDGET,
                                            text_color="#E0F0FF",
                                            border_color=BORDER_COLOR, border_width=1,
                                            corner_radius=8,
                                            state="disabled")
        self._dec_textbox.pack(fill="x", padx=24, pady=(0, 8))

        # ── Copia + Salva
        row3 = ctk.CTkFrame(frame, fg_color="transparent")
        row3.pack(fill="x", padx=24, pady=(0, 14))
        GlowButton(row3, text="📋 Copia",
                   command=self._copy_decoded,
                   width=110, height=34, fg_color=BG_WIDGET,
                   hover_color="#243040", text_color="#C8D8E8",
                   border_color=BORDER_COLOR).pack(side="left", padx=(0, 8))
        GlowButton(row3, text="💾 Salva .txt",
                   command=self._save_decoded_txt,
                   width=130, height=34, fg_color=BG_WIDGET,
                   hover_color="#243040", text_color="#C8D8E8",
                   border_color=BORDER_COLOR).pack(side="left")

        self._dec_status = ctk.CTkLabel(frame, text="",
                                         font=ctk.CTkFont("Consolas", 11),
                                         text_color=ACCENT_CYAN)
        self._dec_status.pack(padx=24, pady=(0, 16), anchor="w")

        return frame

    # ─────────────── CALLBACK ENCODE ───────────────
    def _clear_enc_placeholder(self, _):
        current = self._enc_textbox.get("1.0", "end-1c")
        if current == "Inserisci qui il testo da nascondere…":
            self._enc_textbox.delete("1.0", "end")

    def _browse_encode_image(self):
        path = filedialog.askopenfilename(
            title="Seleziona immagine PNG di copertura",
            filetypes=[("Immagini PNG", "*.png")]
        )
        if path:
            self._encode_img = pathlib.Path(path)
            self._enc_img_label.configure(text=f"  {self._encode_img.name}")

    def _load_txt_encode(self):
        path = filedialog.askopenfilename(
            title="Carica file .txt",
            filetypes=[("File di testo", "*.txt")]
        )
        if not path:
            return
        p = pathlib.Path(path)
        # Controllo limite 2 MB
        if p.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            self._show_upgrade_popup("file superiori a 2 MB")
            return
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Errore lettura", str(e))
            return
        self._enc_textbox.delete("1.0", "end")
        self._enc_textbox.insert("1.0", text)
        self._enc_status.configure(text=f"✔ Testo caricato da: {p.name}", text_color=ACCENT_GREEN)

    def _run_encode(self):
        if not self._encode_img:
            messagebox.showwarning("Attenzione", "Seleziona prima un'immagine PNG di copertura.")
            return

        secret = self._enc_textbox.get("1.0", "end-1c").strip()
        if not secret or secret == "Inserisci qui il testo da nascondere…":
            messagebox.showwarning("Attenzione", "Inserisci o carica il testo segreto da nascondere.")
            return

        # Controllo limite dimensione testo
        text_bytes = secret.encode("utf-8")
        if len(text_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            self._show_upgrade_popup("testi superiori a 2 MB")
            return

        out_path = filedialog.asksaveasfilename(
            title="Salva immagine PNG codificata",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"stegavault_{self._encode_img.stem}.png",
        )
        if not out_path:
            return

        out_path = pathlib.Path(out_path)
        self._enc_status.configure(text="⏳ Elaborazione in corso…", text_color=ACCENT_YELLOW)
        self.update_idletasks()

        _secret_len = len(secret.encode("utf-8"))

        def _task():
            try:
                encode_lsb(self._encode_img, secret, out_path)
                self._stat_encode_ok  += 1
                self._stat_bytes_hidden += _secret_len
                self._enc_status.configure(
                    text=f"✔ Immagine salvata: {out_path.name}  [{_secret_len:,} byte nascosti]",
                    text_color=ACCENT_GREEN
                )
            except Exception as exc:
                self._stat_encode_err += 1
                self._enc_status.configure(text="✖ Errore", text_color=ACCENT_RED)
                messagebox.showerror("Errore Encode", str(exc))

        threading.Thread(target=_task, daemon=True).start()

    # ─────────────── CALLBACK DECODE ───────────────
    def _browse_decode_image(self):
        path = filedialog.askopenfilename(
            title="Seleziona immagine PNG codificata",
            filetypes=[("Immagini PNG", "*.png")]
        )
        if path:
            self._decode_img = pathlib.Path(path)
            self._dec_img_label.configure(text=f"  {self._decode_img.name}")
            self._dec_status.configure(text="")

    def _run_decode(self):
        if not self._decode_img:
            messagebox.showwarning("Attenzione", "Seleziona prima un'immagine PNG.")
            return

        self._dec_status.configure(text="⏳ Decodifica in corso…", text_color=ACCENT_YELLOW)
        self._dec_textbox.configure(state="normal")
        self._dec_textbox.delete("1.0", "end")
        self._dec_textbox.configure(state="disabled")
        self.update_idletasks()

        def _task():
            try:
                result = decode_lsb(self._decode_img)
                self._stat_decode_ok += 1
                self._stat_bytes_extracted += len(result.encode("utf-8"))
                self._dec_textbox.configure(state="normal")
                self._dec_textbox.insert("1.0", result)
                self._dec_textbox.configure(state="disabled")
                self._dec_status.configure(
                    text=f"✔ Estratti {len(result):,} caratteri  ({len(result.encode('utf-8')):,} byte)",
                    text_color=ACCENT_CYAN
                )
            except Exception as exc:
                self._stat_decode_err += 1
                self._dec_status.configure(text="✖ Nessun payload trovato.", text_color=ACCENT_RED)
                messagebox.showerror("Errore Decode", str(exc))

        threading.Thread(target=_task, daemon=True).start()

    def _copy_decoded(self):
        text = self._dec_textbox.get("1.0", "end-1c")
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._dec_status.configure(text="✔ Testo copiato negli appunti.", text_color=ACCENT_CYAN)

    def _save_decoded_txt(self):
        text = self._dec_textbox.get("1.0", "end-1c")
        if not text:
            messagebox.showwarning("Attenzione", "Nessun testo da salvare.")
            return
        path = filedialog.asksaveasfilename(
            title="Salva testo estratto",
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt")],
            initialfile="stegavault_output.txt",
        )
        if path:
            pathlib.Path(path).write_text(text, encoding="utf-8")
            self._dec_status.configure(text=f"✔ Salvato: {pathlib.Path(path).name}",
                                        text_color=ACCENT_CYAN)

    # ────────────────── PANNELLO STATISTICHE ──────────────────
    def _build_stats_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=BG_PANEL,
                              corner_radius=12,
                              border_color=BORDER_COLOR, border_width=1)

        ctk.CTkLabel(frame,
                     text="📊  STATISTICHE DI SESSIONE",
                     font=ctk.CTkFont("Consolas", 15, weight="bold"),
                     text_color=ACCENT_YELLOW).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(frame,
                     text="Contatori aggiornati in tempo reale per questa sessione. Si azzerano alla chiusura del programma.",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=TEXT_DIM, wraplength=580, justify="left").pack(anchor="w", padx=24, pady=(0, 10))

        sep = ctk.CTkFrame(frame, height=1, fg_color=BORDER_COLOR)
        sep.pack(fill="x", padx=24, pady=(0, 18))

        # Griglia 2x3 di card statistiche
        grid = ctk.CTkFrame(frame, fg_color="transparent")
        grid.pack(fill="x", padx=24)
        grid.columnconfigure((0, 1, 2), weight=1, uniform="col")

        def stat_card(parent, row, col, icon, label, var_name, color):
            card = ctk.CTkFrame(parent, fg_color=BG_WIDGET, corner_radius=10,
                                 border_color=BORDER_COLOR, border_width=1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont("Consolas", 22)).pack(pady=(14, 2))
            val_lbl = ctk.CTkLabel(card, text="0",
                                    font=ctk.CTkFont("Consolas", 26, weight="bold"),
                                    text_color=color)
            val_lbl.pack()
            ctk.CTkLabel(card, text=label,
                          font=ctk.CTkFont("Consolas", 9),
                          text_color=TEXT_DIM, wraplength=130, justify="center").pack(pady=(2, 14))
            setattr(self, var_name, val_lbl)

        stat_card(grid, 0, 0, "🔒", "ENCODE riusciti",   "_sv_enc_ok",   ACCENT_GREEN)
        stat_card(grid, 0, 1, "🔓", "DECODE riusciti",   "_sv_dec_ok",   ACCENT_CYAN)
        stat_card(grid, 0, 2, "📦", "Byte nascosti",     "_sv_bytes_h",  ACCENT_GREEN)
        stat_card(grid, 1, 0, "✖",  "Errori ENCODE",     "_sv_enc_err",  ACCENT_RED)
        stat_card(grid, 1, 1, "✖",  "Errori DECODE",     "_sv_dec_err",  ACCENT_RED)
        stat_card(grid, 1, 2, "📤", "Byte estratti",     "_sv_bytes_e",  ACCENT_CYAN)

        sep2 = ctk.CTkFrame(frame, height=1, fg_color=BORDER_COLOR)
        sep2.pack(fill="x", padx=24, pady=(18, 12))

        # Sezione wallet con copia grande
        wallet_section = ctk.CTkFrame(frame, fg_color=BG_WIDGET,
                                       corner_radius=10, border_color=BORDER_COLOR, border_width=1)
        wallet_section.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkLabel(wallet_section,
                     text="₿  Supporta il progetto con una donazione",
                     font=ctk.CTkFont("Consolas", 12, weight="bold"),
                     text_color=ACCENT_YELLOW).pack(pady=(14, 4))

        wallet_row = ctk.CTkFrame(wallet_section, fg_color="transparent")
        wallet_row.pack(pady=(0, 14))

        ctk.CTkLabel(wallet_row,
                     text=WALLET_ADDRESS,
                     font=ctk.CTkFont("Consolas", 11),
                     text_color="#C8D8E8").pack(side="left", padx=(16, 12))

        self._stats_copy_btn = ctk.CTkButton(
            wallet_row,
            text="📋  Copia Wallet",
            width=160, height=34,
            font=ctk.CTkFont("Consolas", 11, weight="bold"),
            fg_color="#1A2B1A", hover_color="#223322",
            text_color=ACCENT_GREEN,
            border_color=ACCENT_GREEN, border_width=1,
            corner_radius=8,
            command=self._copy_wallet_stats,
        )
        self._stats_copy_btn.pack(side="left", padx=(0, 16))

        return frame

    def _copy_wallet_stats(self):
        self.clipboard_clear()
        self.clipboard_append(WALLET_ADDRESS)
        self._stats_copy_btn.configure(text="✔  Copiato!", text_color=ACCENT_YELLOW,
                                        border_color=ACCENT_YELLOW)
        self.after(2500, lambda: self._stats_copy_btn.configure(
            text="📋  Copia Wallet", text_color=ACCENT_GREEN, border_color=ACCENT_GREEN))

    def _refresh_stats(self):
        def fmt_bytes(n):
            if n < 1024: return f"{n} B"
            elif n < 1024**2: return f"{n/1024:.1f} KB"
            else: return f"{n/1024**2:.2f} MB"
        self._sv_enc_ok.configure(text=str(self._stat_encode_ok))
        self._sv_dec_ok.configure(text=str(self._stat_decode_ok))
        self._sv_enc_err.configure(text=str(self._stat_encode_err))
        self._sv_dec_err.configure(text=str(self._stat_decode_err))
        self._sv_bytes_h.configure(text=fmt_bytes(self._stat_bytes_hidden))
        self._sv_bytes_e.configure(text=fmt_bytes(self._stat_bytes_extracted))

    # ─────────────── POPUP UPGRADE ───────────────
    def _show_upgrade_popup(self, feature: str):
        popup = ctk.CTkToplevel(self)
        popup.title("Funzione Expert")
        popup.geometry("480x240")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_PANEL)
        popup.grab_set()

        ctk.CTkLabel(popup,
                     text="⚡  FUNZIONE NON DISPONIBILE",
                     font=ctk.CTkFont("Consolas", 16, weight="bold"),
                     text_color=ACCENT_YELLOW).pack(pady=(24, 8))
        ctk.CTkLabel(popup,
                     text=f"Il supporto per {feature}\nè disponibile nella versione Expert.",
                     font=ctk.CTkFont("Consolas", 12),
                     text_color="#C8D8E8",
                     justify="center").pack(pady=(0, 8))
        ctk.CTkLabel(popup,
                     text="Contatta lo sviluppatore o visita il sito per aggiornare la licenza.",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=TEXT_DIM,
                     wraplength=420, justify="center").pack(pady=(0, 16))
        GlowButton(popup, text="Chiudi", command=popup.destroy,
                   width=120, height=36, fg_color=BG_WIDGET,
                   hover_color="#243040", text_color="#C8D8E8",
                   border_color=BORDER_COLOR).pack()

    # ─────────────── SECURITY TIPS ROTATION ───────────────
    def _start_tip_rotation(self):
        self._show_next_tip()

    def _show_next_tip(self):
        tip = next(self._tip_cycle)
        self._tip_label.configure(text=tip)
        self._tip_job = self.after(8000, self._show_next_tip)


# ─────────────────────────────────────────────────────────────
#  APPLICAZIONE PRINCIPALE
# ─────────────────────────────────────────────────────────────
class StegaVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(820, 580)
        self.configure(fg_color=BG_DARK)

        # Icona (facoltativa – ignora errori se non trovata)
        try:
            icon_path = pathlib.Path(sys._MEIPASS) / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass

        # Container unico che occupa tutta la finestra
        self._container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self._container.pack(fill="both", expand=True)

        # Pre-crea entrambe le schermate (evita lag al momento della transizione)
        self._main_screen = MainAppScreen(self._container)
        self._disclaimer  = DisclaimerScreen(self._container,
                                              on_accept=self._accept_disclaimer)

        # Mostra solo il disclaimer all'avvio
        self._disclaimer.pack(fill="both", expand=True)

    def _accept_disclaimer(self):
        """Nasconde il disclaimer e mostra l'app principale."""
        self._disclaimer.pack_forget()
        self._main_screen.pack(fill="both", expand=True)


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = StegaVaultApp()
    app.mainloop()
