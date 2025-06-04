import os
import io
import sounddevice as sd
import soundfile as sf
import autopep8
import subprocess
import time
import elevenlabs
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
    

    
    
    def speak(self, words):
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


    def speak_opening_line(self, id = 1, filename = r"C:\Users\anant\OneDrive\Documents\Desktop\Jarvis\Ai_helper\output.mp3"):
        if id == 1:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], check=True)
        said = self.record_until_silence()
        
    def record_until_silence(self):
        print("Recording started! Speak your phrase...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            # This listens until you pause talking (VAD kicks in here)
            audio = self.recognizer.listen(source)
        print("Recording stopped automatically (silence detected).")
        try:
            transcription = self.recognizer.recognize_google(audio)
            print("you said:", transcription)
            answer = self.jarvis.respond(transcription)
            print(answer.get("text"))
            self.speak(answer.get("text"))
            print(answer.get("action"))
            contiued_convo = self.check_for_continued_talking()
            if contiued_convo is not False:
                self.conversation(contiued_convo)
        except sr.UnknownValueError:
            print("Sorry, couldn't understand that.")

        except sr.RequestError:
            print("API error.")

    def check_for_continued_talking(self, time=3):
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source=source)
                try:
                    print("starts recording")
                    audio = self.recognizer.listen(source, timeout=3)
                    print("finished recording")
                except sr.WaitTimeoutError:
                    print("No speech detected (timeout).")
                    
                    return False
                
            try:
                text = self.recognizer.recognize_google(audio)
                print("speech Detected Conversation Continues")
                return text
            except:
                print("no speech detected")
                return False
            
    def conversation(self, user_speech):
        convo_cont = True
        while convo_cont:
            response = self.jarvis.respond(user_speech)
            self.speak(response.get("text"))
            print(response.get("action"))
            text = self.check_for_continued_talking()
            if text is not False:
                user_speech = text
                continue
            else:
                break


if __name__ == "__main__":
    speech = TexttoSpeech()
    what_they_want = input("what do you want it to say: ")
    start = time.perf_counter()  
    speech.speak(what_they_want)
    elapsed = time.perf_counter() - start 
    print(elapsed)

