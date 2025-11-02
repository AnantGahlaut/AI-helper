import sys
sys.path.append("..")
from src.Speech import Speech
import time

def test_speech_initialization():
    """Test initialization of the Speech class."""
    start_time = time.time()
    speech_instance = Speech()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Initialization time: {elapsed_time:.2f} seconds")
    assert speech_instance is not None
    assert hasattr(speech_instance, "speak")

def test_speech_speak():
    """Test the speak method of the Speech class."""
    speech_instance = Speech()
    start_time = time.time()
    speech_instance.speak("test speak method")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Speak method time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    test_speech_initialization()
    test_speech_speak()





