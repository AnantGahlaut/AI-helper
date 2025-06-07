import collections
import sounddevice as sd
import webrtcvad
import numpy as np
import speech_recognition as sr
import time

vad = webrtcvad.Vad(2)  # Aggressiveness: 0-3
recognizer = sr.Recognizer()

sample_rate = 16000
frame_duration_ms = 20
frame_size = int(sample_rate * frame_duration_ms / 1000)  # 320 samples per frame
sample_width = 2  # 16-bit audio
channels = 1

def frame_generator():
    with sd.InputStream(channels=channels, samplerate=sample_rate, dtype='int16', blocksize=frame_size) as stream:
        while True:
            audio = stream.read(frame_size)[0]
            volume = np.linalg.norm(audio) / frame_size
            print(f"Volume: {volume:.2f}")  # should spike when you talk
            yield audio.tobytes()


def is_speech(frame):
    return vad.is_speech(frame, sample_rate)

def collect_voiced_frames():
    buffer = []
    silence_count = 0
    speech_count = 0
    max_silence_frames = 3  # 100ms of silence before stopping

    for frame in frame_generator():
        if is_speech(frame):
            buffer.append(frame)
            speech_count += 1
            silence_count = 0
        else:
            if speech_count >= 4:
                silence_count += 1
                if silence_count > max_silence_frames:
                    break
                buffer.append(frame)  # include trailing silence to not cut off words

    return b''.join(buffer)

def transcribe_audio(audio_bytes):
    audio_data = sr.AudioData(audio_bytes, sample_rate, sample_width)
    try:
        text = recognizer.recognize_google(audio_data)
        print(f"[JARVIS]: {text}")
    except sr.UnknownValueError:
        print("[JARVIS]: Sorry, couldn't understand that.")
    except sr.RequestError as e:
        print(f"[JARVIS]: API error: {e}")

# 🔁 Real-time loop
while True:
    print("🎧 Listening...")
    raw_audio = collect_voiced_frames()
    print("🛑 Speech ended. Transcribing...")
    transcribe_audio(raw_audio)
