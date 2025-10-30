import sys
sys.path.append("..")
from jarvis.Jarvis import Jarvis
import time

def test_jarvis_initialization():
    start_time = time.time()
    jarvis_instance = Jarvis()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Initialization time: {elapsed_time:.2f} seconds")
    assert jarvis_instance is not None
    assert hasattr(jarvis_instance, "client")
    assert jarvis_instance.client is not None
    assert hasattr(jarvis_instance, "respond")

def test_jarvis_backend():
    jarvis_instance = Jarvis()
    start_time = time.time()
    response = jarvis_instance.respond("What is the capital of France?")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Response time: {elapsed_time:.2f} seconds")
    assert isinstance(response.get("text"), str)
    print(f"Response: {response.get('text')}")


if __name__ == "__main__":
    test_jarvis_initialization()
    test_jarvis_backend()