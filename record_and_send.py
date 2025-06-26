import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import requests
import os
import simpleaudio as sa  # pip install simpleaudio

# ✅ Settings
SAMPLE_RATE = 16000
DURATION = 6  # seconds
RAILWAY_API_URL = "https://your-project-name.up.railway.app"  # 🔁 Replace with your real Railway URL
BEEP_FILE_PATH = "beep.wav"


# ✅ Play beep before recording
def play_beep():
    try:
        wave_obj = sa.WaveObject.from_wave_file(BEEP_FILE_PATH)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        print(f"⚠️ Could not play beep sound: {e}")


# ✅ Record audio from mic
def record_audio():
    print("🎤 Speak now...")
    play_beep()
    recording = sd.rec(int(DURATION * SAMPLE_RATE),
                       samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, SAMPLE_RATE, recording)
    return temp_file.name


# ✅ Send audio to /transcribe/ and get transcript
def send_audio_get_transcript(file_path):
    url = f"{RAILWAY_API_URL}/transcribe/"
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            print("📡 Sending audio to API for transcription...")
            response = requests.post(url, files=files, timeout=30)
        response.raise_for_status()
        return response.json().get("text")
    except requests.RequestException as e:
        print(f"❌ Error during transcription request: {e}")
        return None


# ✅ (Optional) Send transcript to AI and get reply
def send_text_get_ai_reply(text):
    url = f"{RAILWAY_API_URL}/ai-reply/"
    try:
        print("🤖 Sending text to AI for reply...")
        response = requests.post(url, json={"text": text}, timeout=30)
        response.raise_for_status()
        return response.json().get("reply")
    except requests.RequestException as e:
        print(f"❌ Error during AI reply request: {e}")
        return None


# ✅ Main Loop
if __name__ == "__main__":
    while True:
        try:
            audio_file = record_audio()
            transcript = send_audio_get_transcript(audio_file)
            os.remove(audio_file)

            if transcript:
                print(f"📝 Transcript:\n{transcript}")
                ai_reply = send_text_get_ai_reply(transcript)
                if ai_reply:
                    print(f"💬 AI Reply:\n{ai_reply}")
                else:
                    print("⚠️ No AI reply received.")
            else:
                print("⚠️ No transcription received.")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        cont = input("\nPress Enter to record again or type 'q' to quit: ").strip().lower()
        if cont == 'q':
            print("👋 Exiting. Goodbye!")
            break
