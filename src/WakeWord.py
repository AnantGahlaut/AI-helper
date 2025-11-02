import pyaudio
import pvporcupine
import struct
import os
from dotenv import load_dotenv
import Speech as Speech

class WakeWordDetector:
    """
    WakeWordDetector Class

    This class handles continuous wake word detection using Picovoice's Porcupine engine 
    and acts as the entry point for activating the speech assistant. Once the wake word 
    is detected, it triggers the Speech module to begin interaction with the user.

    Key Features:
    - **Wake Word Detection:** Continuously listens for a pre-defined wake word 
    (default: "porcupine") or a custom keyword file.
    - **Audio Handling:** Uses PyAudio to capture microphone input in real-time with 
    proper buffering for Porcupine processing.
    - **Speech Activation:** Upon detection, triggers the Speech class to play an opening 
    line and start listening for user commands.
    - **Thread-Safe Integration:** Can be combined with other threaded speech operations 
    without blocking.
    - **Resource Management:** Cleanly releases audio and Porcupine resources on exit.

    Usage:
        detector = WakeWordDetector(access_key=ACCESS_KEY, keyword_path=KEYWORD_PATH)
        detector.listen()

    This class is intended to be the always-on "ear" for your AI assistant, 
    activating interaction only when the user says the wake word.
    """

    def __init__(self, access_key, keyword_path=None, sensitivity=0.3):
        """Initialize WakeWordDetector with Porcupine and PyAudio"""
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path] if keyword_path else None,
            keywords=["porcupine"] if not keyword_path else None,
            sensitivities=[sensitivity]
        )

        self.speech = Speech.Speech()
        

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Audio stream configuration
        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
            input_device_index=None  # Use default input device
        )
        
    def listen(self):
        """Listen for wake word and trigger callback when detected"""
        print("Listening for wake word...")
        #blob_thread = threading.Thread(target=self.speech.blob.start, daemon=True)
        #blob_thread.start()
        self.speech.speak("Jarvis Initialized")
        
        try:
            while True:
                # Read audio frame from stream
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Process with Porcupine
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    if self.speech.interupt_listening is not True:
                        print("\nWake word detected!")
                        self.on_wake_word_detected()
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.cleanup()
            
    def on_wake_word_detected(self):
        """Callback when wake word is detected"""
        self.speech.speak_opening_line()
    
    def cleanup(self):
        """Release resources"""
        if hasattr(self, 'stream'):
            self.stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()


if __name__ == '__main__':
    class WakeWord(WakeWordDetector):
        def on_wake_word_detected(self):
            pass
    
    load_dotenv()

    ACCESS_KEY = os.getenv("PORCUPINE_API_KEY")
    
    KEYWORD_PATH = "resources\wakeword.ppn"  
    
    detector = WakeWord(access_key=ACCESS_KEY, keyword_path=KEYWORD_PATH)
    detector.listen()