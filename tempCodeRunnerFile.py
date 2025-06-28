# ============================================
# 🧪 MAIN DEV ENTRY — Voice-Based Case Tester
# ============================================

import asyncio
import os
import winsound
from engine.llm_patient_groq import get_patient_reply_async, generate_examiner_comment
from runner.runner_globals import SESSION_LOG, reset_patient_memory
from runner.case_loader import load_case_by_keyword
from runner.stt_module import transcribe_from_mic

# ============================================
# 🧠 Simple Case Picker by Keyword
# ============================================


def ask_case_keyword():
    keyword = input(
        "🔍 Enter case keyword or number (e.g., 002, mi, herpes): ").strip().lower()
    return keyword

# ============================================
# 🚀 MAIN FUNCTION
# ============================================


async def run_case():
    print("🩺 UKMLA OSCE - Voice Simulation Tester\n")

    # Step 1: Pick Case
    keyword = ask_case_keyword()
    case = load_case_by_keyword(keyword)

    if not case:
        print("❌ No matching case found.")
        return

    print(f"\n📁 Loaded: {case.get('station_name')} — {case.get('diagnosis')}")
    print(f"📖 Complaint: {case.get('presenting_complaint')[0]}")
    print("===========================================\n")

    # Step 2: Doctor-Patient Voice Chat
    while True:
        print("\n🎙️ Your Turn (Doctor)")
        print("🎤 Speak now... ", end="")
        winsound.PlaySound("beep.wav", winsound.SND_FILENAME)

        doctor_input = transcribe_from_mic(duration=8)
        print(f"🩺 You (Doctor): {doctor_input}")

        if doctor_input.strip().lower() in ["exit", "quit", "x"]:
            break

        reply = await get_patient_reply_async(doctor_input, case)

        print(f"🗣️ Patient: {reply}")
        SESSION_LOG["questions"].append(doctor_input)

    # Step 3: Feedback
    print("\n📊 Generating feedback...")
    feedback = generate_examiner_comment(SESSION_LOG, case)
    print("\n🧑‍⚖️ Examiner Feedback:\n")
    print(feedback)

    reset_patient_memory()

# ============================================
# ✅ MAIN ENTRY
# ============================================

if __name__ == "__main__":
    asyncio.run(run_case())
