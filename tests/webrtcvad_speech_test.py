import pyaudio
import sounddevice as sd
import webrtcvad
import numpy as np

vad = webrtcvad.Vad(2)

FRAME_DURATION = 20  # ms
SAMPLE_RATE = 16000
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16
SAMPLE_WIDTH = 2 

def is_speech(frame_bytes):
    return vad.is_speech(frame_bytes, SAMPLE_RATE)

def frame_generator():
    with sd.InputStream(
        channels=1,
        samplerate=SAMPLE_RATE,
        dtype='int16',
        blocksize=FRAME_SIZE
    ) as stream:
        while True:
            audio, _ = stream.read(FRAME_SIZE)   # audio is a numpy array
            assert audio.dtype == np.int16
            frame_bytes = audio.tobytes()
            volume = np.linalg.norm(audio) / FRAME_SIZE
            print(f"Volume: {volume:.2f}, Speech? {is_speech(frame_bytes)}")
            yield frame_bytes

# test loop
for frame in frame_generator():
    pass
