# ============================================
# ✅ FILE: stt_api.py
# ✅ PURPOSE: FastAPI backend for mic-to-text
# ============================================

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
import uvicorn
import tempfile

# Load Whisper model (use 'base' or 'small' for speed)
# You can try "int8_float16" on GPU if needed
model = WhisperModel("base", compute_type="int8")

app = FastAPI()


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Transcribe
        segments, _ = model.transcribe(tmp_path)
        text = " ".join([seg.text for seg in segments])
        return {"transcription": text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
