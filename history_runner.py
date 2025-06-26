# ============================================
# ✅ UKMLA HISTORY RUNNER (v1.4) — Async fixed for sync listen_and_transcribe
# ============================================

import os
import sys
import asyncio
from datetime import datetime, timedelta
from case_loader import load_case, get_case_by_name
from groq_ai import get_patient_reply, adjust_prompt_for_phase
from runner_globals import SESSION_LOG, reset_patient_memory
from feedback import generate_examiner_comment
import traceback
import pyttsx3

# Import your new speech_module with Edge TTS and sync speech_recognition
from speech_module_whisper import listen_and_transcribe, speak

# Initialize pyttsx3 engine (if you want to keep previous TTS, else remove this)
_engine = pyttsx3.init()


def custom_excepthook(exctype, value, tb):
    print("🚨 Uncaught exception:", exctype, value)
    traceback.print_exception(exctype, value, tb)


sys.excepthook = custom_excepthook

# ============================================
# ✅ Phase Logic
# ============================================


async def run_phase(phase_name, duration, case):
    print(
        f"\n🔄 Starting phase: {phase_name.upper()} ({duration.total_seconds()} seconds)", flush=True)
    start_time = datetime.now()
    end_time = start_time + duration
    last_spoke_time = datetime.now()

    if phase_name == "transition":
        await speak("We have reviewed your history. I will now explain the findings.")
        await asyncio.sleep(2)

    while datetime.now() < end_time:
        await asyncio.sleep(0.1)
        try:
            # Run the synchronous listen_and_transcribe in a thread for async compatibility
            doctor_input = await asyncio.to_thread(listen_and_transcribe, phase_name)
        except Exception as e:
            print(f"❌ Error during listen_and_transcribe: {e}", flush=True)
            doctor_input = ""

        if not doctor_input or doctor_input.strip() == "":
            silent_for = (datetime.now() - last_spoke_time).total_seconds()
            if phase_name == "transition" and silent_for > 3:
                print("⏭️ Silent during transition phase, skipping early...", flush=True)
                break
            if silent_for > 10:
                await speak("Are you ready to continue, doctor?")
                await asyncio.sleep(1)
            continue

        last_spoke_time = datetime.now()
        print(f"👨‍⚕️ Doctor: {doctor_input}", flush=True)

        try:
            SESSION_LOG["questions"].append({
                "phase": phase_name,
                "timestamp": datetime.now().isoformat(),
                "input": doctor_input
            })
            print("🧠 Logged doctor question to SESSION_LOG.", flush=True)
        except Exception as e:
            print(f"❌ Failed to log SESSION_LOG question: {e}", flush=True)

        try:
            adjusted_input = adjust_prompt_for_phase(phase_name, doctor_input)
            patient_reply = get_patient_reply(adjusted_input, case, phase_name)
        except Exception as e:
            print(f"❌ Error getting patient reply: {e}", flush=True)
            patient_reply = "Sorry, I did not understand the question."

        print(f"🗣️ Patient: {patient_reply}", flush=True)
        try:
            await speak(patient_reply)
        except Exception as e:
            print(f"❌ Error during speak(): {e}", flush=True)

    print(f"✅ Phase {phase_name.upper()} complete.", flush=True)

# ============================================
# ✅ Run Full History Station (8 minutes approx)
# ============================================


async def run_history_station(case):
    if not case:
        print("❌ No case data loaded, cannot run station.", flush=True)
        return

    print(f"🧾 Case ID: {case.get('case_id')}", flush=True)
    print(f"📋 Station: {case.get('station_name')}", flush=True)

    reset_patient_memory()
    print("✅ Case loaded, starting interactive history-taking simulation...", flush=True)

    phase_durations = {
        "history": timedelta(minutes=8),      # 8 minutes history taking
        "transition": timedelta(seconds=10),
        "ice": timedelta(seconds=10),
        "management": timedelta(seconds=10),
    }

    await run_phase("history", phase_durations["history"], case)
    await run_phase("transition", phase_durations["transition"], case)
    await run_phase("ice", phase_durations["ice"], case)
    await run_phase("management", phase_durations["management"], case)

    print("\n🏁 History Station session completed.\n", flush=True)
    print("🧠 Final SESSION_LOG:", SESSION_LOG, flush=True)

    feedback = generate_examiner_comment(SESSION_LOG, case)
    print("\n🧑‍⚖️ Examiner Feedback:\n", feedback, flush=True)

# ============================================
# ✅ Case Selection Logic
# ============================================


def select_case_from_folder():
    print("📁 Selecting case from folder...", flush=True)
    BASE_FOLDER = "history_based/general_medicine/cases/chest_pain"
    search_term = "herpes_zoster_002"  # Change as needed

    try:
        matching_cases = [f[:-5] for f in os.listdir(BASE_FOLDER)
                          if f.endswith(".json") and search_term in f.lower()]
        if not matching_cases:
            print("❌ No matching cases found.", flush=True)
            return None

        selected_name = matching_cases[0]
        case = get_case_by_name(BASE_FOLDER, selected_name)

        if isinstance(case, dict):
            print(f"✅ Case selected: {case.get('case_id')}", flush=True)
            return case
        else:
            print("❌ Loaded case is not a dict.", flush=True)
            return None

    except Exception as e:
        print(f"🔥 Exception during case loading: {e}", flush=True)
        return None

# ============================================
# ✅ Script Entry Point
# ============================================


if __name__ == "__main__":
    print("🚀 Starting history_runner.py (v1.4 - Async fixed for sync listen_and_transcribe)", flush=True)
    selected_case = select_case_from_folder()
    if selected_case:
        asyncio.run(run_history_station(selected_case))
    else:
        print("❌ No case selected. Exiting program.", flush=True)
