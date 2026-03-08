import time
import subprocess
from piper.voice import PiperVoice

MODEL_PATH = "/home/swh/piper-voices/de_DE-thorsten-low.onnx"
TEXT = "Hallo, ich bin dein Raspberry Pi."
AUDIO_DEVICE = "plughw:CARD=AUDIO,DEV=0"

print("Loading model...")
t0 = time.time()
voice = PiperVoice.load(MODEL_PATH)
print(f"load: {time.time() - t0:.3f}s")

sample_rate = voice.config.sample_rate
print(f"sample_rate: {sample_rate}")

print("Synthesizing + playing raw audio...")
t1 = time.time()

aplay = subprocess.Popen(
    [
        "aplay",
        "-D", AUDIO_DEVICE,
        "-r", str(sample_rate),
        "-f", "S16_LE",
        "-t", "raw",
        "-"
    ],
    stdin=subprocess.PIPE
)

total_bytes = 0
for audio_bytes in voice.synthesize_stream_raw(TEXT):
    total_bytes += len(audio_bytes)
    aplay.stdin.write(audio_bytes)

aplay.stdin.close()
aplay.wait()

print(f"audio bytes: {total_bytes}")
print(f"total synth+play: {time.time() - t1:.3f}s")