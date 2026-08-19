# 🤖 Jarvis OS - AI Desktop Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green?style=for-the-badge&logo=python)
![OpenAI Whisper](https://img.shields.io/badge/OpenAI-Whisper-black?style=for-the-badge&logo=openai)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

> A voice-activated, continuous-listening AI desktop assistant featuring Windows system automation and a cinematic, telemetry-rich Pygame HUD.

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Security & Privacy](#-security--privacy)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)

---

## 🔭 Overview

Jarvis OS is a hands-free, voice-activated desktop assistant built in Python. It features a continuous speech pipeline using OpenAI's Whisper, real-time intelligence powered by Groq-hosted LLMs, and high-fidelity speech synthesis via ElevenLabs. The system is packaged within a retro-futuristic, dynamic Pygame HUD displaying live hardware telemetry, audio spectrum visualizers, and responsive mouse parallax controls.


<!-- ![Jarvis HUD Demo](link-to-your-image-or-gif.gif) -->

---

## ✨ Key Features

* **Continuous Voice Interaction:** "Wake up, Jarvis" hands-free activation utilizing local `openai-whisper` transcription.
* **Dynamic Pygame HUD:** A 2D holographic interface featuring:
  * Live CPU/RAM telemetry overlays.
  * Real-time audio spectrum equalizers and sine-wave rings.
  * Interactive mouse parallax effects.
* **Local System Automation:** 
  * Execute shell commands to open Windows directories (Downloads, Desktop).
  * Launch local applications (Brave, VS Code, Spotify).
  * Trigger deep-search Microsoft Store URI protocols.
* **Persistent Memory:** Utilizes local SQLite databases to maintain conversational context across sessions.
* **Self-Healing Error Catching:** Built-in Python traceback interceptors to prevent UI crashes during execution anomalies.

---

## 🛡️ Security & Privacy

This application is designed with strict local-first processing for system commands. 
* **API Key Management:** API keys for Groq and ElevenLabs are required but must be stored locally. **Never commit your API keys to version control.** 
* **Data Handling:** Persistent memory (`jarvis_memory.db`) is stored locally on the host machine and is isolated from external cloud syncs.

---

## ⚙️ Prerequisites

Ensure you have the following installed and configured before running the OS:

* **Python 3.10** or higher.
* [Groq API Key](https://console.groq.com/) for the LLM logic engine.
* [ElevenLabs API Key](https://elevenlabs.io/) for high-fidelity text-to-speech.

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/Jarvis-OS.git](https://github.com/YOUR-USERNAME/Jarvis-OS.git)
   cd Jarvis-OS
2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys:**
   Open `jarvis_os.py` and replace the placeholder variables with your actual API keys:
   ```python
   GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
   ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY_HERE"
   ELEVENLABS_VOICE_ID = "YOUR_ELEVENLABS_VOICE_ID_HERE"
   ```

---

## 🎧 Usage

Run the main script from your terminal:
```bash
python jarvis_os.py
```
Wait for the terminal to display `[LISTENING FOR WAKE WORD]`, and simply say **"Wake up, Jarvis"** to initiate the continuous conversation loop. Say **"Go to sleep"** to return the system to standby.

---
**Author:** Ajin A
