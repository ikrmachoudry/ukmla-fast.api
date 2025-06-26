from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import tempfile
from faster_whisper import WhisperModel

app = FastAPI()

# ===========================
# ✅ Whisper Model Init (once)
# ===========================
model = WhisperModel("base.en", compute_type="int8")

# ===========================
# ✅ Ping Route
# ===========================
@app.get("/ping")
def ping():
    return {"message": "pong"}

# ===========================
# ✅ Real Transcription Endpoint
# ===========================
@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        segments, _ = model.transcribe(tmp_path)
        full_text = " ".join([segment.text for segment in segments])
        print("📄 Transcription result:", full_text)
        return {"text": full_text}
    
    except Exception as e:
        print("❌ Error in transcription:", str(e))
        return {"error": str(e)}

# ===========================
# ✅ AI Reply Endpoint
# ===========================
class AIRequest(BaseModel):
    text: str

@app.post("/ai-reply/")
async def get_ai_reply(payload: AIRequest):
    from groq_ai import get_patient_reply
    try:
        print("Received text for AI:", payload.text)
        reply = get_patient_reply(payload.text, case=None, phase="history")
        print("Reply generated:", reply)
        return {"reply": reply}
    except Exception as e:
        print("❌ Error in AI reply:", str(e))
        return {"error": str(e)}
