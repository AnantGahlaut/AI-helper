import webrtcvad
import collections
import pyaudio
import struct

# Constants
FRAME_DURATION = 20  # ms
SAMPLE_RATE = 16000
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Setup
vad = webrtcvad.Vad(2)  # 0-3: Aggressiveness
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=SAMPLE_RATE, input=True,
                    frames_per_buffer=FRAME_SIZE)

# Ring buffer for holding previous frames
ring_buffer = collections.deque(maxlen=10)
speaking = False

print("Listening for speech...")

try:
    while True:
        frame = stream.read(FRAME_SIZE)
        is_speech = vad.is_speech(frame, SAMPLE_RATE)

        if is_speech:
            ring_buffer.append(frame)
            if not speaking:
                print("🎙️ Start speaking!")
                speaking = True
        else:
            if speaking:
                print("⏹️ Done speaking!")
                speaking = False

except KeyboardInterrupt:
    print("Exiting...")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
