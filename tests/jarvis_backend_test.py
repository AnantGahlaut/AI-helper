import sys
sys.path.append("..")
from src.Backend import Backend
import time

def test_jarvis_initialization():
    """Test initialization of the Jarvis Backend class."""
    start_time = time.time()
    jarvis_instance = Backend()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Initialization time: {elapsed_time:.2f} seconds")
    assert jarvis_instance is not None
    assert hasattr(jarvis_instance, "client")
    assert jarvis_instance.client is not None
    assert hasattr(jarvis_instance, "respond")

def test_jarvis_backend():
    """Test the respond method of the Jarvis Backend class."""
    jarvis_instance = Backend()
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