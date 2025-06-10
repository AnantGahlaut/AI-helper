import pyaudio
import pvporcupine
import struct
import os
import Speech

class WakeWordDetector:
    def __init__(self, access_key, keyword_path=None, sensitivity=0.3):
        # Initialize Porcupine
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path] if keyword_path else None,
            keywords=["porcupine"] if not keyword_path else None,
            sensitivities=[sensitivity]
        )

        self.texttospeech = Speech.TexttoSpeech()
        
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
        self.texttospeech.speak("Jarvis Initialized")
        
        try:
            while True:
                # Read audio frame from stream
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Process with Porcupine
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    print("\nWake word detected!")
                    self.on_wake_word_detected()
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.cleanup()
            
    def on_wake_word_detected(self):
        self.texttospeech.speak_opening_line()
    
    def cleanup(self):
        """Release resources"""
        if hasattr(self, 'stream'):
            self.stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()


if __name__ == '__main__':
    ACCESS_KEY = "YoJJ2GN4CRSCbFssd9B53Rdn8jwEp0DcWSapSf/qE/56coAbPf/faw=="
    
    KEYWORD_PATH = "Ai_helper\wakeword.ppn"  
    
    detector = WakeWordDetector(access_key=ACCESS_KEY, keyword_path=KEYWORD_PATH)
    detector.listen()