# ⬡ Stega Vault — Hide Secrets Inside Images

> **"A picture is worth a thousand words. With Stega Vault, it can also hide them."**

![Version](https://img.shields.io/badge/version-1.0.0-00FF9C?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)
![Offline](https://img.shields.io/badge/100%25-Offline-00FF9C?style=for-the-badge)
![Free](https://img.shields.io/badge/Base%20Edition-Free-blue?style=for-the-badge)

---

## 🤔 What does this program actually do?

Imagine you have a **normal photo** — maybe a picture of a sunset, a cat, or a city skyline.

Stega Vault lets you **hide a secret message inside that photo**, in a way that:

- ✅ The photo looks **completely normal** to anyone who sees it
- ✅ You can **send it to someone** via email or USB drive
- ✅ Only the person with Stega Vault can **extract the hidden message**

This technique is called **steganography** — the art of hiding information in plain sight. It has been used by spies, journalists, and privacy advocates for centuries. Stega Vault brings it to your desktop with a simple, modern interface.

---

## 🧠 How is this different from encryption?

Great question.

| | What it does | What others see |
|---|---|---|
| **Encryption** (e.g. ZIP with password) | Scrambles the text so no one can read it | A suspicious locked file — people *know* something is hidden |
| **Steganography** (Stega Vault) | Hides the text inside an image | A completely normal photo — nobody suspects anything |

**The best protection? Use both.** Encrypt your text first, then hide it with Stega Vault.

---

## 🖼️ How does hiding inside an image work? (Simple version)

Every image on your screen is made of millions of tiny coloured dots called **pixels**.

Each pixel has three colour values: **Red, Green, Blue** — each a number from 0 to 255.

Stega Vault changes the **very last digit** of some of these numbers to encode your message.

```
Before:   Red = 11001010   ← last digit is 0
After:    Red = 11001011   ← last digit changed to 1  (your secret bit!)
```

The colour difference is **0.4%** — completely invisible to the human eye.

When you want to read the message back, Stega Vault reads all those last digits and reconstructs your text automatically.

---

## 🆚 Why Stega Vault and not something else?

There are other steganography tools out there. Here is why Stega Vault is better for most people:

| Other Tool | The Problem | Stega Vault Instead |
|---|---|---|
| **OpenStego** | Needs Java installed, clunky interface from the 90s | Works out of the box, modern dark design |
| **SilentEye** | Last updated in 2012, broken on modern systems | Actively maintained and working |
| **Steghide** | Command line only — you have to type scary commands | Friendly graphical interface, just click |
| **Online tools** (websites) | Your secret text travels through someone else's server | 100% offline — your data never leaves your computer |
| **StegSolve** | Only for analysing images, cannot hide anything | Full encode + decode + statistics in one app |

---

## ✅ What can Stega Vault do?

### 🔒 ENCODE — Hide a message
1. Pick any PNG image (your "cover" image)
2. Type your secret message, or load a `.txt` file
3. Click **ENCODE** and save the new image
4. Send that image to whoever you want — it looks perfectly normal

### 🔓 DECODE — Read a hidden message
1. Open the image you received (must be a PNG encoded with Stega Vault)
2. Click **DECODE**
3. Your secret message appears instantly

### 📊 STATS — See what you have done this session
- How many messages you have hidden
- How many you have decoded
- Total bytes of data hidden and extracted
- Error count

### 💡 Security Tips (always visible in the sidebar)
The app shows rotating cybersecurity advice — simple, practical tips to keep your communications safe.

---

## ⚠️ Important things to know before using it

### PNG only — never JPEG

```
✅  photo.png    →  Safe, works perfectly
✅️. photo.jpg    →  Will DESTROY your hidden message
❌  photo.webp   →  Will DESTROY your hidden message
```

WEBP compress images by slightly changing pixel colours to save space.
This **destroys** the hidden bits. **Always use PNg and JPEG

---

### Never send the image as a photo via messaging apps

These apps **automatically recompress** every photo you send, which destroys the hidden message.

```

✅  Email     →  any attachment     →  Safe
✅  Telegram  →  send as FILE       →  Safe  ← important difference!
✅  USB drive / SD card             →  Safe
✅  Google Drive / Dropbox link     →  Safe
```

---

### How much text can I hide?

It depends on the image size. Bigger image = more space for text.

| Image Size | Approx. how much text fits |
|---|---|
| 800 × 600 | ~175,000 characters (about 100 pages of a book) |
| 1920 × 1080 (Full HD) | ~760,000 characters (about 430 pages) |
| 3840 × 2160 (4K) | ~3,000,000 characters (about 1,700 pages) |

---

## 🚀 How to install and run — step by step

### Step 1 — Install Python (if you don't have it)

Go to 👉 **https://www.python.org/downloads/**

Click the big yellow **"Download Python"** button and run the installer.

> 🔴 **IMPORTANT:** During installation, tick the box that says **"Add Python to PATH"** before clicking Install. If you miss this, Python won't work from the terminal.

To check it worked, open **Command Prompt** (search "cmd" in the Start menu) and type:

```
python --version
```

You should see something like `Python 3.11.4`. Any version **3.9 or higher** is fine.

---

### Step 2 — Install the two required libraries

In the same Command Prompt window, paste this and press Enter:

```
pip install customtkinter pillow
```

This downloads two things:
- **customtkinter** — creates the modern dark window interface
- **pillow** — reads and writes image files

You only need to do this once.

---

### Step 3 — Run the app

Navigate to the folder where you saved `stega_vault.py`, then run:

```
python stega_vault.py
```

**Or:** right-click the folder, open a terminal there, and type the command above.

The app window will open. Read the disclaimer, click **"Accept & Continue"**, and you are ready to go.

---

## 📦 I want a double-click .exe file (Windows only)

If you do not want to open a terminal every time, you can turn the app into a normal Windows program.

**Step 1** — In Command Prompt, run:
```
pip install pyinstaller
```

**Step 2** — Then run:
```
pyinstaller --onefile --windowed --name "StegaVault" stega_vault.py
```

**Step 3** — Wait 1–3 minutes, then look inside a new folder called `dist/`:
```
dist/
  StegaVault.exe   ← this is your program!
```

Double-click `StegaVault.exe` like any other program. Done.
You can move this `.exe` anywhere — no Python needed on the target machine.

---

## 🔒 What are the limits of the free version?

Stega Vault Base Edition is **completely free**. It has two limits:

| What is limited | Limit | Is it enough? |
|---|---|---|
| Text / file size | Max **2 MB** | Yes — that is over 1,000 pages of plain text |
| File type you can hide | **`.txt` files only** | For hiding secret messages, yes |

If you try to go beyond these limits, the app will show you a message explaining how to upgrade to Expert Edition.

---

## 🛡️ 7 security tips you should know

These same tips rotate inside the app sidebar.

1. **Always use PNG.** JPEG destroys hidden data. No exceptions.
2. **Send as a document, not a photo** — even in Telegram or Signal, use the "file" option not the camera roll.
3. **Do not post the same image in two places** — someone with the original could compare and detect changes.
4. **Encrypt your text before hiding it** — Stega Vault hides your text but does not scramble it. If someone finds it, they can read it. Use a ZIP with password or VeraCrypt to add encryption first.
5. **Avoid uploading to social media** — every platform recompresses your images automatically.
6. **Use a password manager** like Bitwarden (free) or KeePass. Never reuse passwords.
7. **Enable two-factor authentication (2FA)** on every important account (email, banking, etc.).

---

## ❓ Common questions

**Q: Can anyone tell there is a hidden message just by looking at the image?**
A: No. The changes are invisible to the human eye. The image looks identical.

**Q: What if I accidentally delete the encoded image?**
A: The message is lost. Stega Vault cannot recover it. Always keep a backup of the PNG file.

**Q: Does it work on Mac and Linux too?**
A: Yes. Run `python stega_vault.py` on any system. The `.exe` builder is Windows-only.

**Q: Is my text sent anywhere? Does it connect to the internet?**
A: Never. Stega Vault is 100% offline. Nothing leaves your computer.

**Q: Why is the encoded image slightly larger than the original?**
A: PNG saves every pixel exactly as-is (it is "lossless"), including your hidden bits. This causes a small size increase. This is completely normal.

**Q: Can I hide a photo inside another photo?**
A: Not in Base Edition. Expert Edition supports hiding any file type (images, PDFs, ZIP files, etc.).

**Q: The image I received does not decode. Why?**
A: Most likely the image was recompressed somewhere along the way (e.g. it was sent as a WhatsApp photo). Ask the sender to resend it as a **file/document attachment**.

---

## 💰 Support the project

Stega Vault Base Edition is free and always will be.
If it is useful to you, a small crypto donation keeps development going:

```
₿  Bitcoin (BTC) wallet address:
bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

You can **copy this address with one click** inside the app:
- Look for the green **📋 Copia** button in the left sidebar
- Or go to the **📊 Stats** tab for the larger copy button

---

## ⚖️ Legal notice

Stega Vault is a tool for **legal, educational, and personal privacy use only.**

The developer is **not responsible** for any illegal, harmful, or unethical use of this software.

By clicking "Accept & Continue" in the app, you confirm that:
- You have read and understood the full disclaimer shown at startup
- You will not use Stega Vault for illegal activities of any kind
- You take full personal responsibility for how you use this tool

---

## 📁 What is in this project

```
stega_vault.py    ← The entire application (a single Python file)
README.md         ← This guide you are reading right now
```

---

<div align="center">

**Stega Vault v1.0.0  —  Base Edition**

*Hide in plain sight. Stay private. Stay safe.*

⬡

</div>
