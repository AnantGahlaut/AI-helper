Jarvis — Lightweight AI Voice Assistant

Overview

Jarvis is a lightweight AI voice assistant built in Python that lets you 
control your computer using natural speech. It listens for your commands, 
processes them with an intelligent backend, and executes tasks like launching apps, 
running PowerShell commands, or automating workflows—all while running efficiently in the background.

Features
- 🧠 Conversational AI — Understands natural language and responds intelligently.
- ⚡ Lightweight & Efficient — Runs quietly in the background with minimal CPU and memory.
- 🧩 Automation Ready — Launch apps, trigger workflows, and execute PowerShell commands hands-free.
- 🔇 Interruptible Voice Output — Pause or stop speech instantly.
- 🔊 Noise Filtering — Handles background noise for cleaner recognition.
- 🧰 Customizable Skills — Add your own commands and extend functionality easily.


Voice Input & Recognition

- 🎙️ SpeechRecognition | PyAudio | SoundDevice | SoundFile | webrtcvad | pvporcupine

Text-to-Speech & Output

- 🗣️ pyttsx3 | 🎤 ElevenLabs API | pydub 

Backend & Utilities

- 💻 PowerShell | webbrowser | dotenv | numpy

### Setup 

1. Clone this repo.
```
git clone https://github.com/AnantGahlaut/AI-helper.git
```
2. Install requirements.
```
pip install -r requirements.txt
```

3. Make the env files with API keys and Paths


### API keys

1. Create an **OpenRouter** account and generate an API key. Save it as `OPENROUTER_API_KEY`.
2. Create **ElevenLabs** credentials:
   - Create two ElevenLabs accounts and generate one API key in each. (This is because each account only gives you 15k tokens per month; 2 accounts will make sure you never run out of tokens, with failover capabilities.)
   - Save them as `ELEVENLABS_KEY_1` and `ELEVENLABS_KEY_2` (and `ELEVENLABS_VOICE_1`, `ELEVENLABS_VOICE_2` for voice IDs).
3. Get a **Porcupine / Picovoice** AccessKey:
   - Register at Picovoice, create/access a key, and download any `.ppn` wake-word file(s) you want to use.
   - Save the key as `PORCUPINE_ACCESS_KEY` and put keyword files in e.g. `./porcupine/`.
4. Create a `.env` file in the project root with these entries:

```python
# API KEYS
OPENROUTER_API_KEY    = "sk-xx-xx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ELEVEN_LABS_API_KEY_1 = "sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ELEVEN_LABS_API_KEY_2 = "sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
PORCUPINE_API_KEY     = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/xx/xxxxxxx/x"

# VOICE IDS
VOICE_ID_1 = "xxxxxxxxxxxxxxxxxxxx"
VOICE_ID_2 = "xxxxxxxxxxxxxxxxxxxx"

# Absolute Paths (These are for the app opening)
CHROME_PATH   = "C:\Program Files\Google\Chrome\Application\chrome.exe"
VSCODE_PATH   = "C:\Users\YOURUSERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe"
SPOTIFY_PATH  = "explorer shell:appsFolder\SpotifyAB.xxxxxxxxxxxxxxxxxxx!Spotify"
OUTLOOK_PATH  = "C:\Program Files\WindowsApps\Microsoft.OutlookForWindows_1.xx_x64__xxxxx\olk.exe"
WHATSAPP_PATH = "C:\Program Files\WindowsApps\xxxxxx.WhatsAppDesktop_2.2522.2.xxxxxxxxx\WhatsApp.exe"
# You can add more as you like, but don't forget to include the new info in the Backend.py file
```


### How To Use

1. Run `main.py` in `src`
2. Wait for the System to initialize. Once it does that, it will say Jarvis Initialized.
3. Now you can say Jarvis, and if the system understands you, it will say Yes, Sir.
4. Right after Jarvis finishes, it starts recording for speech. If you don't say anything, or it doesn't recognize speech, it will go into dormant mode, waiting for you to say the wake word again
5. Once you finish speaking, it will transcribe your speech, feed it into the AI backend, get a response, and use the TTS system to respond.
6. If you want to interrupt Jarvis in the middle of its speaking, you can js repeat "Jarvis", the wake word, and it will stop the audio.
7. Once it is done speaking, it will go through the same cycle of listening for a response from you; if it doesn't get one, it will go back to dormant mode.




