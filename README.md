# OMNIVOICE - AI Voice Agent
**Team Name:** UNCENSORED RUNTIME

## 🚀 Project Overview
A real-time AI voice consultant for luxury real estate. The system listens to user speech, processes intent using Google Gemini 3 Flash, and responds with low-latency audio using MacOS native TTS.

## 🏗️ Architecture
1. **User Call** -> Twilio Media Stream
2. **Twilio** -> WebSocket (ngrok) -> FastAPI Server
3. **FastAPI** -> Faster-Whisper (Transcription)
4. **Text** -> Gemini 1.5 Flash (Brain)
5. **Response** -> System Audio ('Say' command)

## 📺 Demo Recording

See OmniVoice in action! This recording demonstrates the real-time transcription 
https://drive.google.com/file/d/13vykAGrRcTLYXXNsMhphsmCD8cdsMKvy/view?usp=sharing

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Core Framework:** FastAPI
- **AI Model:** Google Gemini 3 Flash
- **Transcription:** Faster-Whisper
- **Tunneling:** Ngrok

## ⚙️ Setup Instructions
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

2. **Set up Environment:**
   Create a .env file in the root directory:
   ```bash
   GEMINI_API_KEY=your_key_here

4. **Run the Server:**
   ```bash
   python -m src.main

5. **Start Ngrok:**
   Expose your local port 8000:
   ```bash
   ngrok http 8000

