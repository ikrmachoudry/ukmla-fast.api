# main_fastapi.py

import asyncio
from fastapi import FastAPI
from runner.case_loader import load_case_by_keyword
from runner.runner_globals import SESSION_LOG, reset_patient_memory
from runner.stt_module import transcribe_from_mic_vad
from runner.tts_module import speak_text
from engine.llm_patient_groq import get_patient_reply_async, generate_examiner_comment

app = FastAPI()


@app.get("/")
def home():
    return {"message": "UKMLA AI Voice Sim Running!"}


@app.get("/run")
async def run_interactive_case(keyword: str = "herpes"):
    case = load_case_by_keyword(keyword)
    if not case:
        return {"error": "❌ Case not found."}

    # 🎤 Doctor Speaks
    doctor_input = transcribe_from_mic_vad()
    print(f"🩺 Doctor: {doctor_input}")

    if doctor_input.strip().lower() in ["exit", "quit", "x"]:
        return {"message": "🔚 Session ended."}

    # 🤖 Patient Replies
    reply = await get_patient_reply_async(doctor_input, case, phase="history")
    print(f"🗣️ Patient: {reply}")
    await speak_text(reply)

    SESSION_LOG["questions"].append(doctor_input)

    return {
        "doctor_said": doctor_input,
        "patient_replied": reply,
        "status": "✅ Interaction complete"
    }


@app.get("/feedback")
def get_feedback(keyword: str = "herpes"):
    case = load_case_by_keyword(keyword)
    feedback = generate_examiner_comment(SESSION_LOG, case)
    reset_patient_memory()
    return {"feedback": feedback}
