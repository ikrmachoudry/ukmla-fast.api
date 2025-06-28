# ✅ FILE: history_runner.py
# ✅ PURPOSE: Run one interaction loop for the History station

from runner.case_loader import load_case
from runner.st_module import record_voice, transcribe_audio_google
from runner.tts_module import reply_with_voice
from llm.pt_groq import ask_groq
from time import time
import asyncio
from engine.llm_patient_groq import get_patient_reply_async


# ✅ MEDIA TRIGGER function
def detect_media_trigger(transcript: str) -> str | None:
    keywords = {
        "chest": "media/general_med/shingles.jpg",
        "eye": "media/eye/fundus.jpg",
        "ear": "media/ent/ear_image.jpg"
    }
    for word, path in keywords.items():
        if word.lower() in transcript.lower():
            return path
    return None

# ✅ MAIN function for one user turn
def run_history_turn(case_name, level, phase="history"):
    """
    Run one interaction in the History station.
    
    Args:
        case_name (str): Name of the case, like 'chest_pain'
        level (str): Case level, like 'b'
        phase (str): Either 'history' or 'management'

    Returns:
        None
    """

    # ✅ Step 1: Load case JSON
    case_data = load_case(case_name, level, category="history_based")

    # ✅ Step 2: Define phase-based mic duration
    PHASE_DURATION = {
        "history": 8,
        "management": 12
    }
    duration = PHASE_DURATION.get(phase, 6)

    # ✅ Step 3: Record user input and transcribe
    audio_file = record_voice(duration=duration)
    transcript = transcribe_audio_google(audio_file)
    print(f"👨‍⚕️ Doctor: {transcript}")

    # ✅ Step 4: Check if media should be shown
    media_file = detect_media_trigger(transcript)
    if media_file:
        print(f"🖼️ Media triggered: {media_file}")

    # ✅ Step 5: Generate AI reply from Groq
    ai_reply = ask_groq(transcript, case_context=case_data)
    print(f"🧠 Groq says: {ai_reply}")

    # ✅ Step 6: Speak AI reply aloud
    asyncio.run(reply_with_voice(ai_reply))
