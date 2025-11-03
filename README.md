# Jarvis — Lightweight AI Voice Assistant

> Your personal voice-powered desktop assistant built with Python.

---

## 🚀 Overview
Jarvis is a lightweight AI voice assistant built in Python that lets you control your computer using natural speech.  
It listens for your commands, processes them with an intelligent backend, and executes tasks like launching apps,  
running PowerShell commands, or automating workflows — all while staying efficient in the background.

---

## ✨ Features
- 🧠 **Conversational AI** — Understands natural language and responds intelligently  
- ⚡ **Lightweight & Efficient** — Runs quietly with minimal CPU/memory usage  
- 🧩 **Automation Ready** — Launch apps, trigger workflows, execute PowerShell commands  
- 🔇 **Interruptible Voice Output** — Pause or stop speech instantly  
- 🔊 **Noise Filtering** — Handles background noise for clearer recognition  
- 🧰 **Customizable Skills** — Easily extend with new commands  

---

## 🧩 Voice & Tech Stack

### 🎙️ Voice Input & Recognition  
`SpeechRecognition` • `PyAudio` • `SoundDevice` • `SoundFile` • `webrtcvad` • `pvporcupine`

### 🗣️ Text-to-Speech & Output  
`pyttsx3` • `ElevenLabs API` • `pydub`

### 💻 Backend & Utilities  
`PowerShell` • `webbrowser` • `dotenv` • `numpy`•`openAI`

---

## ⚙️ Setup

**1️⃣ Clone the Repo** 
```bash
git clone https://github.com/AnantGahlaut/AI-helper.git
```
**2️⃣ Install requirements**
```bash
pip install -r requirements.txt
```
**3️⃣ Add API keys**

You will have to go to websites and create accounts to get api keys.

For eleven labs (the TTS engine), I have set up two keys as a failover system. 
```python
# API KEYS
OPENROUTER_API_KEY    = "sk-xx-xx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ELEVEN_LABS_API_KEY_1 = "sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ELEVEN_LABS_API_KEY_2 = "sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
PORCUPINE_API_KEY     = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/xx/xxxxxxx/x"

# VOICE IDS FOR ELEVEN LABS (each ID is for a separate account)
VOICE_ID_1 = "xxxxxxxxxxxxxxxxxxxx" # API key #1
VOICE_ID_2 = "xxxxxxxxxxxxxxxxxxxx" # API key #2

# Absolute Paths (These are for the app opening)
CHROME_PATH   = "C:\Program Files\Google\Chrome\Application\chrome.exe"
VSCODE_PATH   = "C:\Users\YOURUSERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe"
SPOTIFY_PATH  = "explorer shell:appsFolder\SpotifyAB.xxxxxxxxxxxxxxxxxxx!Spotify"
OUTLOOK_PATH  = "C:\Program Files\WindowsApps\Microsoft.OutlookForWindows_1.xx_x64__xxxxx\olk.exe"
WHATSAPP_PATH = "C:\Program Files\WindowsApps\xxxxxx.WhatsAppDesktop_2.2522.2.xxxxxxxxx\WhatsApp.exe"
# You can add more as you like, but don't forget to include the new info in the Backend.py file
```

--- 

### How To Use it

**1️⃣ Run the Main Script**
```bash
python src/main.py
```
**2️⃣ Wait for initialization**

   Jarvis will say:
   
   "Jarvis Initialized"
   
**3️⃣ Say the Wake Word**

   Say "Jarvis" and it will respond, "Yes, Sir?"
   
**4️⃣ Give a command**
   Speak naturally. Jarvis will(in a matter of seconds):
   - 🎧 Record your speech
   - 📝 Transcribe it
   - 🧠 Send it to the AI backend
   - 🗣️ Respond using TTS (text-to-speech)
     
**5️⃣ Interupt (optional)**

   While Jarvis is speaking, say "Jarvis" again.
   
   It will immediately stop talking and start listening for the next command.
   
**6️⃣ Conversating Loop**

   When Jarvis finishes speaking, it will record for about 6 seconds, if it detects speech, it transcribes it and starts the process again.
   
   If no input is detected, it returns to a dormant mode until you say the wake word ("Jarvis") again.

   





