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
import struct
import time
import pyttsx3
import elevenlabs
import numpy as np
from pydub.utils import mediainfo
from pydub import AudioSegment
import pvporcupine
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import Jarvis


class TexttoSpeech:


    def __init__(self, api_key_no=2):

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

        self.porcupine = pvporcupine.create(
            access_key="YoJJ2GN4CRSCbFssd9B53Rdn8jwEp0DcWSapSf/qE/56coAbPf/faw==",
            keyword_paths=["Ai_helper\wakeword.ppn" ] if "Ai_helper\wakeword.ppn" else None,
            keywords=["porcupine"] if not "Ai_helper\wakeword.ppn"  else None,
            sensitivities=[0.3]
        )

        self.interupt_listening = False

        self.audio = pyaudio.PyAudio()

        self.continue_listen_for_interupt = True
        self.continue_calibrate_noise = True
        self.interrupted = False

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.mic_lock = threading.Lock()
        self.jarvis = Jarvis.Jarvis()

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
    
    def log_function_name(func):
        def wrapper(*args, **kwargs):
            print(f"Calling function: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper

    @log_function_name
    def listen_for_interupt(self):
        
        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
            input_device_index=None 
        )
        try:
            print("listen for interupt")
            self.interupt_listening = True
            while self.continue_listen_for_interupt:
                # Read audio frame from stream
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Process with Porcupine
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    print("\ninterupt detected!")
                    self.interrupted = True
                    self.continue_listen_for_interupt = False
                    self.on_interupt()
                    break 
            print("done listening for interupt")
            self.interupt_listening = False
        except Exception as e:
            print(e)

    @log_function_name
    def on_interupt(self):
        with self.mic_lock:
            self.stop_audio_playback()
            self.record_until_silence()

    @log_function_name
    def stop_audio_playback(self):
            print("Stopping audio playback...")
            self.audio_process.kill() 
            self.audio_process = None
 

    @log_function_name
    def calibrate_noise(self, duration=1):
            with self.mic_lock:
                with self.microphone as source:
                    print("📡 Calibrating for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                    print(f"✅ Energy threshold set to: {self.recognizer.energy_threshold}")

    @log_function_name
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

            duration_str = mediainfo(filename)["duration"]
            duration = float(duration_str)

            self.interrupted = False
            self.continue_listen_for_interupt = True
            self.continue_calibrate_noise = True

            calibration_thread = threading.Thread(target=self.calibrate_noise, args=(duration,), daemon=True)
            calibration_thread.start()

            interupt_thread = threading.Thread(target=self.listen_for_interupt, args= (), daemon=True)
            print("made interupt thread and about to start it")
            interupt_thread.start()

            print(f"time took: {time.time()-self.start}")

            self.audio_process = subprocess.Popen(["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", filename])
            self.audio_process.wait()
            self.continue_listen_for_interupt = False  
            self.continue_calibrate_noise = False


           

    @log_function_name
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
    
    @log_function_name
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

        if self.interrupted is False:
            print(answer.get("action"))
            print("record_until_silence is calling check_for_talking")
            contiued_convo = self.check_for_continued_talking()
            if contiued_convo is not False:
                self.conversation(contiued_convo)

    @log_function_name
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
            
    @log_function_name
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

