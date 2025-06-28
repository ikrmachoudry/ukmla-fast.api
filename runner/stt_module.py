# ✅ FILE: runner/st_module.py
# ✅ PURPOSE: Mic recording + Google STT transcription (NO Whisper)

import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import os

# ✅ RECORD audio from mic and save as WAV


def record_voice(filename="output.wav", duration=5, fs=44100):
    print(f"🎙️ Recording for {duration}s...")
    recording = sd.rec(int(duration * fs), samplerate=fs,
                       channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, recording)
    print(f"✅ Saved: {filename}")
    return filename

# ✅ TRANSCRIBE audio using Google STT


def transcribe_audio_google(filename="output.wav"):
    recognizer = sr.Recognizer()

    if not os.path.exists(filename):
        return "[Audio file not found]"

    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"📝 Transcription: {text}")
        return text
    except sr.UnknownValueError:
        return "[Unrecognized speech]"
    except sr.RequestError as e:
        print(f"❌ Google STT Error: {e}")
        return "[Google STT service unavailable]"

# ✅ COMBINED: Record and transcribe (used in main.py)


def transcribe_from_mic_vad():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening (VAD active)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)  # No time limit, stops on silence

    try:
        return recognizer.recognize_google(audio)
    except Exception as e:
        return f"[STT Error]: {e}"
