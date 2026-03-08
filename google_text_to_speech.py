"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import subprocess
import time
import queue
import threading

# I want tq
text_to_speech_queue = queue.Queue()
speak_queue = queue.Queue()

# Sentences to be synthesized
sentences = [
    "Hallo Freunde bitte gebt uns eine gute Note",
    "Warum ist das so schwer",
    "Wir haben so viel Zeit in dieses Projekt investiert",
    "Sagen sie das hier als letzen Satz"
]


# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="de-DE", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)
# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="de-DE", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)
# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)


def read_sentences():
    """Thread 1: Reads sentences and puts them in text_to_speech_queue"""
    for sentence in sentences:
        print(f"[Reader] Adding to queue: {sentence}")
        text_to_speech_queue.put(sentence)
    text_to_speech_queue.put(None)  # Signal end of queue


def synthesize_speech():
    """Thread 2: Reads from text_to_speech_queue, synthesizes, and puts audio in speak_queue"""
    while True:
        text = text_to_speech_queue.get()
        if text is None:  # End signal
            speak_queue.put(None)
            break
        
        print(f"[Synthesizer] Processing: {text}")
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        print(f"[Synthesizer] Audio synthesized, adding to speak queue")
        speak_queue.put(response.audio_content)


def play_audio():
    """Thread 3: Reads audio from speak_queue and plays it"""
    while True:
        audio_content = speak_queue.get()
        if audio_content is None:  # End signal
            break
        
        print(f"[Player] Playing audio")
        with open("output.wav", "wb") as out:
            out.write(audio_content)
        
        subprocess.run(["aplay", "-D", "plughw:2,0", "output.wav"])
        print(f"[Player] Playback finished")


if __name__ == "__main__":
    start_time = time.time()
    
    # Create and start threads
    thread1 = threading.Thread(target=read_sentences, daemon=False)
    thread2 = threading.Thread(target=synthesize_speech, daemon=False)
    thread3 = threading.Thread(target=play_audio, daemon=False)
    
    thread1.start()
    thread2.start()
    thread3.start()
    
    # Wait for all threads to finish
    thread1.join()
    thread2.join()
    thread3.join()
    
    end_time = time.time()
    print(f"Duration: {end_time - start_time:.3f} seconds")