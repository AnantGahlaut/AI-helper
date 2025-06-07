import pyttsx3
import time

# Initialize the engine
engine = pyttsx3.init()

# Optional: Adjust voice properties
engine.setProperty('rate', 180)     # Speed (words per minute)
engine.setProperty('volume', .8)   # Volume (0.0 to 1.0)

# List available voices (use this to pick your favorite)
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(f"Voice {i}: {voice.name} - {voice.id}")

# Set voice (pick index based on your system, e.g., male/female, English/other lang)
engine.setProperty('voice', voices[0].id)

# 🔊 Say something
start = time.time()
engine.say("Hey, my name is Jarvis I am here to assist you")
engine.runAndWait()
print(time.time()-start)
