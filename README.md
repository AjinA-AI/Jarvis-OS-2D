# Jarvis OS - AI Desktop Assistant

A Python-based, voice-activated AI desktop assistant featuring a fully dynamic Pygame HUD inspired by cinematic interfaces. Jarvis continuously listens in the background, controls local Windows applications, interfaces with LLMs for intelligent responses, and speaks using high-fidelity text-to-speech.

## Features
- **Continuous Voice Interaction:** "Wake up, Jarvis" hands-free activation using OpenAI's Whisper model.
- **Dynamic Pygame HUD:** A 2D holographic interface with live CPU/RAM telemetry, audio spectrum visualizer, and mouse parallax effects.
- **Local System Automation:** Open Windows directories, launch apps, and interact with the Microsoft Store natively.
- **Persistent Memory:** Uses local SQLite to remember conversational context over time.

## Prerequisites
- Python 3.10+
- A Groq API Key for the LLM brain.
- An ElevenLabs API Key for voice generation.

## Usage
Run the main script from your terminal:
\\\ash
python jarvis_os.py
\\\
Wait for the "LISTENING FOR WAKE WORD" prompt, and say "Wake up, Jarvis" to initiate a conversation!

---
**Author:** Ajin A
