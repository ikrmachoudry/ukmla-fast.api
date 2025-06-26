# fastapi_railway.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import tempfile
import openai

app = FastAPI()

# Allow all origins (change for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your OpenAI API key as an environment variable or hardcode here
openai.api_key = "YOUR_OPENAI_API_KEY"


class TextRequest(BaseModel):
    text: str


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        shutil.copyfileobj(file.file, temp_wav)
        temp_filename = temp_wav.name

    # TODO: Replace this with real transcription logic (e.g. Whisper)
    transcription = "Dummy transcription from uploaded audio"

    # Cleanup can be done here if you want
    return {"text": transcription}


@app.post("/ai-reply/")
async def ai_reply(request: TextRequest):
    prompt = request.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Error calling AI: {str(e)}"}
