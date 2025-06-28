# ============================================
# ✅ routes/transcribe_route.py
# ============================================

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from runner import st_module  # This should contain your Google STT logic
import os
import uuid

router = APIRouter()


# ============================================
# ✅ Endpoint: /transcribe/
# ============================================

@router.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Receives audio file from client, passes it to STT module,
    and returns transcribed text.
    """
    try:
        # ✅ Save uploaded file temporarily
        temp_filename = f"temp_audio_{uuid.uuid4().hex}.wav"
        with open(temp_filename, "wb") as buffer:
            buffer.write(await file.read())

        # ✅ Call STT Module
        transcript = st_module.transcribe_audio(temp_filename)

        # ✅ Clean up
        os.remove(temp_filename)

        if not transcript:
            raise HTTPException(
                status_code=500, detail="STT failed to produce transcript.")

        return JSONResponse(content={"transcript": transcript})

    except Exception as e:
        print(f"⚠️ Transcription Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during transcription.")
