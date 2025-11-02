import os
import logging
import webrtcvad
import pyaudio
import sounddevice as sd
import soundfile as sf
import subprocess
import collections
import threading
import struct
import time
import pyttsx3
import numpy as np
from pydub.utils import mediainfo
import pvporcupine
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from Backend import Backend


class Speech:
    """
    Speech Class

    This class provides a comprehensive voice interface for interacting with the Jarvis backend. 
    It handles the complete audio pipeline from wake word detection to speech output, supporting 
    both synchronous and asynchronous operations. 

    Features include:
    - **Wake Word Detection:** Uses pvporcupine to detect a specified wake word and trigger 
    interrupt-driven listening.
    - **Speech Recognition:** Captures audio from the microphone, calibrates for ambient noise, 
    and converts spoken words into text using Google's Speech Recognition API.
    - **Text-to-Speech:** Converts Jarvis responses into audio using ElevenLabs TTS with multiple 
    voice styles and fallback to pyttsx3 when needed.
    - **Interrupt Handling:** While speaking, the class can detect user interruptions and immediately 
    stop playback to respond to new input.
    - **Voice Activity Detection (VAD):** Uses WebRTC VAD to dynamically detect when the user is 
    speaking versus silent, allowing natural conversation flow.
    - **Threaded Operations:** Calibrates ambient noise and listens for interrupts in parallel 
    threads to ensure responsiveness without blocking main execution.
    - **Conversation Loop:** Supports multi-turn conversations by continuously listening for 
    follow-up user input and processing it through the Jarvis backend.
    - **Logging:** Records all major actions, errors, and timing information to log.txt for 
    debugging and performance monitoring.

    Design Notes:
    - API keys and file paths are currently hard-coded; for production, consider using 
    environment variables or a config file.
    - Extensive error handling is implemented for TTS failures and speech recognition issues.
    - Audio playback is managed via subprocesses running ffplay, enabling interruptible audio 
    without blocking Python execution.

    Usage:
    1. Initialize the class: `speech = Speech(api_key_no=1 or 2)`
    2. Start a conversation: `speech.speak("Hello Jarvis")`
    3. Jarvis will handle wake word detection, listen for user speech, transcribe it, 
    pass it to the backend, and speak the response.

    Overall, this class serves as a high-level orchestration layer for voice interaction, 
    providing a near real-time, responsive AI assistant experience.
    """


    def __init__(self, api_key_no=2):
        """Initialize the Speech class, setting up audio interfaces, APIs, and runtime configurations."""

        load_dotenv()

        self.eleven_labs_api_key_1 = os.getenv("ELEVEN_LABS_API_KEY_1")
        self.eleven_labs_api_key_2 = os.getenv("ELEVEN_LABS_API_KEY_2")

        self.voice_id_1 = os.getenv("VOICE_ID_1")
        self.voice_id_2 = os.getenv("VOICE_ID_2")

        if api_key_no == 2: 
            self.client = ElevenLabs(
            api_key= self.eleven_labs_api_key_2,
            )
            self.speak_style = 2
            
        elif api_key_no == 1:
            self.client = ElevenLabs(
            api_key= self.eleven_labs_api_key_1,
            )
            self.speak_style = 1

        self.porcupine = pvporcupine.create(
            access_key="YoJJ2GN4CRSCbFssd9B53Rdn8jwEp0DcWSapSf/qE/56coAbPf/faw==",
            keyword_paths=["resources\wakeword.ppn" ] if "resources\wakeword.ppn" else None,
            keywords=["porcupine"] if not "Ai_helper\wakeword.ppn"  else None,
            sensitivities=[0.3]
        )

        self.interupt_listening = False

        self.audio = pyaudio.PyAudio()

        logging.basicConfig(
            filename="log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        self.continue_listen_for_interupt = True
        self.continue_calibrate_noise = True
        self.interrupted = False

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.mic_lock = threading.Lock()
        self.jarvis = Backend()

        self.engine = pyttsx3.init()
        self.vad = webrtcvad.Vad(3) 
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
        """Decorator that logs the name of any function it wraps when called."""

        def wrapper(*args, **kwargs):
            logging.info(f"Calling function: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper

    @log_function_name
    def listen_for_interupt(self):
        """Continuously listens for the wake word using Porcupine; triggers on_interupt() when detected."""

        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
            input_device_index=None 
        )
        try:
            logging.info("listen for interupt")
            self.interupt_listening = True
            while self.continue_listen_for_interupt:
                # Read audio frame from stream
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Process with Porcupine
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    logging.debug("interupt detected")
                    self.time_to_interupt_time = time.time()
                    self.interrupted = True
                    self.continue_listen_for_interupt = False
                    self.continue_calibrate_noise = False
                    self.on_interupt()
                    break 
            logging.info("done listening for interupt")
            self.interupt_listening = False
        except Exception as e:
            print(e)


    @log_function_name
    def on_interupt(self):
        """Handles the interrupt event by stopping playback and starting a new speech recording session."""

        with self.mic_lock:
            self.stop_audio_playback()
            logging.info("interupt time: ", time.time()-self.time_to_interupt_time)
            self.record_until_silence()


    @log_function_name
    def stop_audio_playback(self):
        """Stops currently playing audio by killing the subprocess running ffplay."""

        logging.WARNING("Stopping audio playback...")
        self.audio_process.kill() 
        self.audio_process = None
 

    @log_function_name
    def calibrate_noise(self, duration=1):
        """Calibrates the speech recognizer to ambient noise to improve transcription accuracy."""

        with self.mic_lock:
            with self.microphone as source:
                print(" Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=.1)
                print(f" Energy threshold set to: {self.recognizer.energy_threshold}")
                logging.info(f" Energy threshold set to: {self.recognizer.energy_threshold}")

    @log_function_name
    def speak(self, words=""):
        """Converts text to speech using ElevenLabs (or fallback to pyttsx3) and plays it, supporting live interrupt detection."""

        print(f"Using speak_style {self.speak_style}")
        self.start = time.time()
        if not isinstance(words, str):
            logging.error("speak method received non-string input")
            raise TypeError("Can only speak type -> str")
        
        advanced_voice = True

        # Speak Style 1 and 2 use ElevenLabs TTS, It switches between the two api keys if one fails
        # Speak Style 3 uses pyttsx3 as a fallback TTS engine
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
                    logging.error("advanced voice is Malfunctioning")
                    print("advanced voice is Malfunctioning")
                    self.engine.say("Advanced Voice is Malfunctioning. Switching to Default")
                    logging.WARNING("Switching to Default Voice")
                    self.engine.runAndWait()
                    self.speak_style = 3
                    self.speak(words)
                    return
                else:
                    print(f"error happened switching voices: {e}")
                    self.engine.say("An error occured. Switching Voices to 2")
                    logging.WARNING("Switching to Voice 2")
                    self.engine.runAndWait()
                    self.speak_style = 2
                    self.speech_error = 1
                    self.client = ElevenLabs(
                    api_key= self.eleven_labs_api_key_2,
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
                    logging.error("advanced voice is Malfunctioning")
                    self.engine.say("Advanced Voice is Malfunctioning. Switching to Default")
                    logging.WARNING("Switching to Default Voice")
                    self.engine.runAndWait()
                    self.speak_style = 3
                    self.speak(words)
                    return
                else:
                    print(f"error happened switching voices: {e}")
                    self.engine.say("An error occured. Switching Voices to 1")
                    logging.WARNING("Switching to Voice 1")
                    self.engine.runAndWait()
                    self.speak_style = 1
                    self.speech_error = 1
                    self.client = ElevenLabs(
                    api_key= self.eleven_labs_api_key_1,
                    )
                    self.speak(words)
                    return
                
        elif self.speak_style == 3:
            self.engine.say(words) 
            self.engine.runAndWait()
            advanced_voice = False


        if advanced_voice:
            # Save audio bytes to a temporary file for playback, then play with ffplay
            filename = "temp_output.mp3"
            with open(filename, "wb") as f:
                f.write(audio_bytes)

            duration_str = mediainfo(filename)["duration"]
            duration = float(duration_str)

            self.interrupted = False
            self.continue_listen_for_interupt = True
            self.continue_calibrate_noise = True

            # Start threads for listening for interupts and calibrating noise
            calibration_thread = threading.Thread(target=self.calibrate_noise, args=(duration,), daemon=True)
            calibration_thread.start()

            interupt_thread = threading.Thread(target=self.listen_for_interupt, args= (), daemon=True)
            print("made interupt thread and about to start it")
            interupt_thread.start()

            print(f"time took to turn text into speach: {time.time()-self.start}")
            logging.info(f"time took to turn text into speach: {time.time()-self.start}")

            if hasattr(self,"response_time"):
                print("total response time:", time.time()-self.response_time)
                logging.info(f"total response time: {time.time()-self.response_time}")

            self.audio_process = subprocess.Popen(["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", filename])
            self.audio_process.wait()
            self.continue_listen_for_interupt = False  
            self.continue_calibrate_noise = False


    @log_function_name
    def speak_opening_line(self, id = 1, filename = r"resources\YesSir.mp3"):
        """Plays an opening voice line (Yes sir) and immediately begins listening for a user response."""

        if id == 1:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], check=True)
        said = self.record_until_silence()
        
    def frame_generator(self):
        """Yields continuous frames of microphone audio data for speech activity detection."""

        with sd.InputStream(
            channels=1,  # VAD likes mono
            samplerate=self.SAMPLE_RATE,
            dtype='int16',
            blocksize=self.FRAME_SIZE
        ) as stream:
            while True:
                audio, _ = stream.read(self.FRAME_SIZE)
                assert audio.dtype == np.int16
                frame_bytes = audio.tobytes()
                volume = np.linalg.norm(audio) / self.FRAME_SIZE
                print(f"Volume: {volume:.2f}, {self.is_speech(frame_bytes)}")
                yield frame_bytes  # always yield bytes

    def is_speech(self, frame_bytes):
        """Returns True if the given audio frame contains speech using the WebRTC VAD."""

        return self.vad.is_speech(frame_bytes, self.SAMPLE_RATE)
    
    def collect_voiced_frames(self, max_loops=60):
        """Collects voiced audio frames until silence is detected or timeout reached, returning raw byte data."""

        buffer = []
        silence_count = 0
        speech_count = 0
        max_silence_frames = 5  # 100ms of silence before stopping
        min_frames = 25

        for i, frame in enumerate(self.frame_generator()):
            if i > max_loops and speech_count == 0:
                print("no speech detected in allotted time")
                logging.info("no speech detected in allotted time")
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
        """Converts raw audio bytes into text using the Google Speech Recognition API."""

        audio_data = sr.AudioData(audio_bytes, self.SAMPLE_RATE, self.SAMPLE_WIDTH)
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("[JARVIS]: Sorry, couldn't understand that.")
            logging.info("Speech Recognition could not understand audio | probably due to not actual speech")
        except sr.RequestError as e:
            print(f"[JARVIS]: API error: {e}")
            logging.error(f"Could not request results from Speech Recognition service; {e}")
        except Exception as e:
            print(e)
            return None
    
    @log_function_name
    def record_until_silence(self):
        """Records user speech until silence, transcribes it, passes it to Jarvis, and speaks the response."""

        print("🎧 Listening...")
        logging.info("Listening for user speech")
        raw_audio = self.collect_voiced_frames()
        print("🛑 Speech ended. Transcribing...")
        logging.info("Speech ended, starting transcription")
        self.transcribe_speech_start = time.time()
        self.response_time = time.time()
        transcription = self.transcribe_audio(raw_audio)
        print("you said:", transcription)
        logging.info(f"User said: {transcription}")
        if transcription is None:
            return None
        answer = self.jarvis.respond_and_act(transcription)

        if transcription is None:
            print("[JARVIS]: Didn't catch that, try again!")
            logging.warning("Transcription returned None | probably due to unclear speech")
            return
        
        print(answer.get("text"))
        logging.info(f"Jarvis response: {answer.get('text')}")
        print(f"time took to transcribe speech: {time.time()-self.transcribe_speech_start}")
        logging.info(f"time took to transcribe speech: {time.time()-self.transcribe_speech_start}")

        self.speak(answer.get("text"))

        if self.interrupted is False:
            print(answer.get("action"))
            contiued_convo = self.check_for_continued_talking()
            if contiued_convo is not False:
                self.conversation(contiued_convo)

    @log_function_name
    def check_for_continued_talking(self):
        """Listens briefly after Jarvis finishes speaking to check if the user continues the conversation."""

        print("checking for continued talking after jarvis response")
        logging.info("checking for continued talking after jarvis response")
        raw_audio = self.collect_voiced_frames()
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
        """Maintains an interactive conversation loop between the user and Jarvis until the user stops speaking."""

        convo_cont = True
        while convo_cont:
            response = self.jarvis.respond_and_act(user_speech)
            self.speak(response.get("text"))
            print(response.get("action"))
            text = self.check_for_continued_talking()
            if text is not False:
                user_speech = text
                continue
            else:
                break


if __name__ == "__main__":
    speech = Speech()
    what_they_want = input("what do you want it to say: ")
    start = time.perf_counter()  
    speech.speak(what_they_want)
    elapsed = time.perf_counter() - start 
    print(elapsed)

