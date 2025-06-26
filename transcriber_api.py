from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()  # ✅ Only one app object — at the top

# ===========================
# ✅ Ping Route
# ===========================
@app.get("/ping")
def ping():
    return {"message": "pong"}

# ===========================
# ✅ Dummy Transcription Endpoint
# ===========================
@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    await file.read()  # Silence warning for now
    return {"text": "Dummy transcription"}

# ===========================
# ✅ AI Reply Endpoint
# ===========================
class AIRequest(BaseModel):
    text: str

@app.post("/ai-reply/")
async def get_ai_reply(payload: AIRequest):
    from groq_ai import get_patient_reply
    try:
        reply = get_patient_reply(payload.text, case=None, phase="history")
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}
