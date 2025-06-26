import requests

# Replace with your actual token
API_TOKEN = "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"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

AUDIO_FILE_PATH = "beep.wav"

with open(AUDIO_FILE_PATH, "rb") as f:
    response = requests.post(
        "https://api-inference.huggingface.co/models/guillaumekln/faster-whisper",
        headers=headers,
        data=f
    )

# Handle and print response
if response.status_code == 200:
    print("✅ Transcription:")
    print(response.json())
else:
    print(f"❌ Error {response.status_code}: {response.text}")
