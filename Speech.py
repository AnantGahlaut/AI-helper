import os
import io
import webrtcvad
import pyaudio
import sounddevice as sd
import soundfile as sf
import autopep8
import subprocess
import collections
import time
import elevenlabs
import numpy as np
from pydub import AudioSegment
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from better_jarvis2 import Jarvis

class TexttoSpeech:


    def __init__(self):

        load_dotenv()

        self.client = ElevenLabs(
          api_key='sk_2dfc4b33dd96eedab9a1a4b80a251d98b386bd1340ff86c2',
          )
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.jarvis = Jarvis()

        self.vad = webrtcvad.Vad(2) 
        self.audio = pyaudio.PyAudio()
        self.ring_buffer = collections.deque(maxlen=10)

        self.FRAME_DURATION = 20  # ms
        self.SAMPLE_RATE = 16000
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION / 1000)
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16
        self.SAMPLE_WIDTH = 2 

        self.start = 0
        
    
    def speak(self, words):
        self.start = time.time()
        if not isinstance(words, str):
            raise TypeError("Can only speak type -> str")
        
        audio_gen = self.client.text_to_speech.convert(
            text=words,
            voice_id="ZQe5CZNOzWyzPSCn5a3c",
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
        )
        
        # Collect chunks into one bytes object
        audio_bytes = b"".join(audio_gen)
        
        filename = "temp_output.mp3"
        with open(filename, "wb") as f:
            f.write(audio_bytes)
        
        proccess = subprocess.Popen(["ffplay", "-autoexit", "-nodisp", filename])
        proccess.wait()
        print(f"time took:{time.time()-self.start}")


    def speak_opening_line(self, id = 1, filename = r"C:\Users\anant\OneDrive\Documents\Desktop\Jarvis\Ai_helper\output.mp3"):
        if id == 1:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], check=True)
        said = self.record_until_silence()
        
        
    def frame_generator(self):
        with sd.InputStream(channels=self.CHANNELS, samplerate=self.SAMPLE_RATE, dtype='int16', blocksize=self.FRAME_SIZE) as stream:
            while True:
                audio = stream.read(self.FRAME_SIZE)[0]
                volume = np.linalg.norm(audio) / self.FRAME_SIZE
                print(f"Volume: {volume:.2f}")  # should spike when you talk
                yield audio.tobytes()

    def is_speech(self, frame):
        return self.vad.is_speech(frame, self.SAMPLE_RATE)
    
    def collect_voiced_frames(self, max_loops=1000):
        buffer = []
        silence_count = 0
        speech_count = 0
        max_silence_frames = 3  # 100ms of silence before stopping
        i = 1
        for frame in self.frame_generator():
            if i > max_loops:
                print("no speech detected in alloted time")
                return None
                break
            if self.is_speech(frame):
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

