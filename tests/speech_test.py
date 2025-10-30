from jarvis.Speech import Speech
import time

def test_speech_initialization():
    start_time = time.time()
    speech_instance = Speech()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Initialization time: {elapsed_time:.2f} seconds")
    assert speech_instance is not None
    assert hasattr(speech_instance, "speak")


def test_speech_speak():
    speech_instance = Speech()
    start_time = time.time()
    speech_instance.speak("test speak method")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Speak method time: {elapsed_time:.2f} seconds")






