import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import tempfile

sample_rate = 16000
duration = 3  # seconds

print("🎙️ Recording for 3 seconds...")
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()
print("✅ Recording done.")

# Save to file
with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
    scipy.io.wavfile.write(f.name, sample_rate,
                           (audio * 32767).astype(np.int16))
    print("🔊 Saved audio to:", f.name)
