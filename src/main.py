import WakeWord
from dotenv import load_dotenv
import os

load_dotenv()
    
ACCESS_KEY = os.getenv("PORCUPINE_API_KEY")

KEYWORD_PATH = "resources\wakeword.ppn" 

detector = WakeWord.WakeWordDetector(access_key=ACCESS_KEY, keyword_path=KEYWORD_PATH)
detector.listen()