from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    await file.read()  # placeholder for real transcription
    return {"text": "Dummy transcription"}


@app.post("/ai-reply/")
async def ai_reply(data: dict):
    text = data.get("text")
    # placeholder for AI reply logic
    return {"reply": f"AI reply for: {text}"}
