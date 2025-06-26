import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile
from faster_whisper import WhisperModel

model = WhisperModel("tiny")


def record_and_transcribe(duration=6, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        filename = f.name
        scipy.io.wavfile.write(filename, sample_rate,
                               (audio * 32767).astype(np.int16))
    print("Transcribing...")
    segments, _ = model.transcribe(filename)
    transcription = " ".join([segment.text for segment in segments])
    print("You said:", transcription)


record_and_transcribe()
