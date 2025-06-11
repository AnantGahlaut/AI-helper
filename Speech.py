import os
import io
import webrtcvad
import pyaudio
import sounddevice as sd
import soundfile as sf
import autopep8
import subprocess
import collections
import threading
import time
import pyttsx3
import elevenlabs
import numpy as np
from pydub.utils import mediainfo
from pydub import AudioSegment
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from better_jarvis2 import Jarvis

class TexttoSpeech:


    def __init__(self, api_key_no=1):

        load_dotenv()

        self.api_key_1 ='sk_2dfc4b33dd96eedab9a1a4b80a251d98b386bd1340ff86c2'
        self.api_key_2 ='sk_a8cf14db90cef0bdbea3052e34f290351d8aff2e223ffac0'

        if api_key_no == 2: 
            self.client = ElevenLabs(
            api_key= self.api_key_2,
            )
            self.speak_style = 2
            
        elif api_key_no == 1:
            self.client = ElevenLabs(
            api_key= self.api_key_1,
            )
            self.speak_style = 1

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.jarvis = Jarvis()

        self.engine = pyttsx3.init()
        self.vad = webrtcvad.Vad(3) 
        self.audio = pyaudio.PyAudio()
        self.ring_buffer = collections.deque(maxlen=10)
                   
        self.FRAME_DURATION = 20  # ms
        self.SAMPLE_RATE = 16000
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION / 1000)
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16
        self.SAMPLE_WIDTH = 2 
        self.speech_error = 0
        self.start = 0
        
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('rate', 180)     # Speed (words per minute)
        self.engine.setProperty('volume', 1.0) 
        self.engine.setProperty('voice', self.voices[0].id)

        self.calibrate_noise()

    def calibrate_noise(self, duration=1):
        with self.microphone as source:
            print("📡 Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"✅ Energy threshold set to: {self.recognizer.energy_threshold}")
    
    def speak(self, words=""):
        print(f"Using speak_style {self.speak_style}")
        self.start = time.time()
        if not isinstance(words, str):
            raise TypeError("Can only speak type -> str")
        
        advanced_voice = True

        if self.speak_style == 1:
            try:
                audio_gen = self.client.text_to_speech.convert(
                    text=words,
                    voice_id="xPGjzNrZAIerjtfmn93E",
                    model_id="eleven_flash_v2_5",
                    output_format="mp3_44100_128",
                )
                self.speech_error = 0 
                audio_bytes = b"".join(audio_gen)
            except Exception as e:
                if self.speech_error == 1:
                    print("advanced voice is Malfunctioning")
                    self.engine.say("Advanced Voice is Malfunctioning. Switching to Default")
                    self.engine.runAndWait()
                    self.speak_style = 3
                    self.speak(words)
                    return
                else:
                    print(f"error happened switching voices: {e}")
                    self.engine.say("An error occured. Switching Voices to 2")
                    self.engine.runAndWait()
                    self.speak_style = 2
                    self.speech_error = 1
                    self.client = ElevenLabs(
                    api_key= self.api_key_2,
                    )
                    self.speak(words)
                    return
        elif self.speak_style == 2:
            try: 
                audio_gen = self.client.text_to_speech.convert(
                    text=words,
                    voice_id="ErXwobaYiN019PkySvjV",
                    model_id="eleven_flash_v2_5",
                    output_format="mp3_44100_128",
                )
                audio_bytes = b"".join(audio_gen)
                print("got here ")
                self.speech_error = 0
            except Exception as e:
                print("second error: ",e)
                if self.speech_error == 1:
                    print(f"advanced voice is Malfunctioning: {e}")
                    self.engine.say("Advanced Voice is Malfunctioning. Switching to Default")
                    self.engine.runAndWait()
                    self.speak_style = 3
                    self.speak(words)
                    return
                else:
                    print(f"error happened switching voices: {e}")
                    self.engine.say("An error occured. Switching Voices to 1")
                    self.engine.runAndWait()
                    self.speak_style = 1
                    self.speech_error = 1
                    self.client = ElevenLabs(
                    api_key= self.api_key_1,
                    )
                    self.speak(words)
                    return

        elif self.speak_style == 3:
            self.engine.say(words) 
            self.engine.runAndWait()
            advanced_voice = False

        if advanced_voice:
            filename = "temp_output.mp3"
            with open(filename, "wb") as f:
                f.write(audio_bytes)

            # 🔍 Get actual duration
            duration_str = mediainfo(filename)["duration"]
            duration = float(duration_str)

            # 🔄 Start noise calibration for exact duration
            calibration_thread = threading.Thread(target=self.calibrate_noise, args=(duration,), daemon=True)
            calibration_thread.start()

            # 🔊 Play it
            print(f"time took: {time.time()-self.start}")
            proccess = subprocess.Popen(["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", filename])
            proccess.wait()
        




    def speak_opening_line(self, id = 1, filename = r"C:\Users\anant\OneDrive\Documents\Desktop\Jarvis\Ai_helper\output.mp3"):
        if id == 1:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], check=True)
        said = self.record_until_silence()
        
        
    def frame_generator(self):
        with sd.InputStream(channels=self.CHANNELS, samplerate=self.SAMPLE_RATE, dtype='int16', blocksize=self.FRAME_SIZE) as stream:
            while True:
                audio = stream.read(self.FRAME_SIZE)[0]
                volume = np.linalg.norm(audio) / self.FRAME_SIZE
                print(f"Volume: {volume:.2f}, {self.is_speech(audio)}")  # should spike when you talk
                yield audio.tobytes()

    def is_speech(self, frame):
        return self.vad.is_speech(frame, self.SAMPLE_RATE)
    
    def collect_voiced_frames(self, max_loops=60):
        buffer = []
        silence_count = 0
        speech_count = 0
        max_silence_frames = 7  # 100ms of silence before stopping
        min_frames = 25

        for i, frame in enumerate(self.frame_generator()):
            if i > max_loops and speech_count == 0:
                print("no speech detected in allotted time")
                return None

            if self.is_speech(frame):
                buffer.append(frame)
                speech_count += 1
                silence_count = 0
            else:
                if speech_count >= 4:
                    silence_count += 1
                    buffer.append(frame)  # only add trailing silence *after* we started speech
                    if silence_count > max_silence_frames and i > 25:
                        break

        return b''.join(buffer) if buffer else None
    
    def transcribe_audio(self, audio_bytes):
        audio_data = sr.AudioData(audio_bytes, self.SAMPLE_RATE, self.SAMPLE_WIDTH)
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("[JARVIS]: Sorry, couldn't understand that.")
        except sr.RequestError as e:
            print(f"[JARVIS]: API error: {e}")
        except Exception as e:
            print(e)
            return None
    

    def record_until_silence(self):
        print("🎧 Listening...")
        raw_audio = self.collect_voiced_frames()
        print("🛑 Speech ended. Transcribing...")
        self.start = time.time()
        transcription = self.transcribe_audio(raw_audio)
        print("you said:", transcription)
        if transcription is None:
            return None
        answer = self.jarvis.respond(transcription)

        if transcription is None:
            print("[JARVIS]: Didn't catch that, try again!")
            return
        
        print(answer.get("text"))
        print(f"time took: {time.time()-self.start}")
        self.speak(answer.get("text"))
        print(answer.get("action"))
        contiued_convo = self.check_for_continued_talking()
        if contiued_convo is not False:
            self.conversation(contiued_convo)

    def check_for_continued_talking(self):
            print("checking for response")
            raw_audio = raw_audio = self.collect_voiced_frames()
            if raw_audio is not None:
                try:
                    transcription = self.transcribe_audio(raw_audio)
                    if transcription is None:
                        return False
                    return transcription
                except Exception as e:
                    print(e)
                    return False
            
            return False
            

    def conversation(self, user_speech):
        convo_cont = True
        while convo_cont:
            response = self.jarvis.respond(user_speech)
            self.speak(response.get("text"))
            print("time Started")
            self.start = time.time()
            print(response.get("action"))
            text = self.check_for_continued_talking()
            if text is not False:
                user_speech = text
                print(f"time took: {time.time()-self.start}")
                continue
            else:
                print(f"time took: {time.time()-self.start}")
                break


if __name__ == "__main__":
    speech = TexttoSpeech()
    what_they_want = input("what do you want it to say: ")
    start = time.perf_counter()  
    speech.speak(what_they_want)
    elapsed = time.perf_counter() - start 
    print(elapsed)

