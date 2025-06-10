import edge_tts
import asyncio
import pyaudio
import time

CHUNK = 1024

async def speak(text):
    start = time.time()
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural", rate="+0%")
    stream = await communicate.stream()

    p = pyaudio.PyAudio()
    audio = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    print(time.time()- start)
    async for chunk in stream:
        if chunk["type"] == "audio":
            audio.write(chunk["data"])

    audio.stop_stream()
    audio.close()
    p.terminate()

asyncio.run(speak("Hey Anant! This is Edge TTS, now with live audio streaming!"))
