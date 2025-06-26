# ============================================
# ✅ UKMLA HISTORY RUNNER (v1.2) — DEBUG MODE
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import os


def safe_main():
    try:
        from case_loader import load_case, get_case_by_name
        from speech_module_whisper import listen_and_transcribe, speak
        from groq_ai import get_patient_reply, adjust_prompt_for_phase
        from runner_globals import SESSION_LOG, reset_patient_memory
        from feedback import generate_examiner_comment

        print("🚀 Starting history_runner.py - immediate start", flush=True)

        # === Stub async functions for debugging, remove if real imported are working ===
        # async def listen_and_transcribe():
        #     print("🎤 [DEBUG] Waiting for doctor input... (simulated)", flush=True)
        #     await asyncio.sleep(1)
        #     return "Tell me more about your chest pain."
        #
        # async def speak(text):
        #     print(f"🗣️ [SPEAK]: {text}", flush=True)
        #     await asyncio.sleep(1)
        #
        # def get_patient_reply(user_input, case, phase):
        #     return f"(Simulated patient reply to: '{user_input}' during {phase})"
        #
        # def adjust_prompt_for_phase(phase, doctor_input):
        #     return doctor_input

        # ============================================
        # ✅ Phase Logic
        # ============================================

        async def run_phase(phase_name, duration, case):
            print(
                f"\n🔄 Starting phase: {phase_name.upper()} ({duration.total_seconds()}s)", flush=True)
            start_time = datetime.now()
            end_time = start_time + duration
            last_spoke_time = datetime.now()

            if phase_name == "transition":
                await speak("We checked your tests. I’ll now explain what we found.")
                await asyncio.sleep(2)

            while datetime.now() < end_time:
                await asyncio.sleep(0.1)
                doctor_input = await listen_and_transcribe()

                if not doctor_input:
                    silent_for = (datetime.now() -
                                  last_spoke_time).total_seconds()
                    if phase_name == "transition" and silent_for > 3:
                        print(
                            "⏭️ Silent during transition. Skipping early...", flush=True)
                        break
                    if silent_for > 4:
                        await speak("Are you okay to continue, doctor?")
                        await asyncio.sleep(1)
                    continue

                last_spoke_time = datetime.now()
                print(f"👨‍⚕️ Doctor: {doctor_input}", flush=True)

                # ✅ Debug SESSION_LOG before use
                try:
                    print("🧠 [DEBUG] SESSION_LOG is accessible. Keys:",
                          SESSION_LOG.keys())
                    SESSION_LOG["questions"].append({
                        "phase": phase_name,
                        "timestamp": datetime.now().isoformat(),
                        "input": doctor_input
                    })
                    print("📝 [DEBUG] Logged question to SESSION_LOG.", flush=True)
                except Exception as e:
                    print("❌ [ERROR] SESSION_LOG append failed:", e, flush=True)

                adjusted_input = adjust_prompt_for_phase(
                    phase_name, doctor_input)
                patient_reply = get_patient_reply(
                    adjusted_input, case, phase_name)

                print(f"🗣️ Patient: {patient_reply}", flush=True)
                await speak(patient_reply)

            print(f"✅ Phase {phase_name.upper()} complete.", flush=True)

        # ============================================
        # ✅ Run Station
        # ============================================

        async def run_history_station(case):
            if not case:
                print("❌ No case data received.", flush=True)
                return

            print(f"🧾 Case ID: {case.get('case_id')}", flush=True)
            print(f"📋 Station: {case.get('station_name')}", flush=True)

            reset_patient_memory()
            print("✅ Case loaded. Starting simulation...", flush=True)

            phase_durations = {
                "history": timedelta(seconds=15),
                "transition": timedelta(seconds=5),
                "ice": timedelta(seconds=10),
                "management": timedelta(seconds=10),
            }

            await run_phase("history", phase_durations["history"], case)
            await run_phase("transition", phase_durations["transition"], case)
            await run_phase("ice", phase_durations["ice"], case)
            await run_phase("management", phase_durations["management"], case)

            print("\n🏁 History Station Finished.\n", flush=True)
            print("🧠 [DEBUG] Final SESSION_LOG:", SESSION_LOG, flush=True)

            feedback = generate_examiner_comment(SESSION_LOG, case)
            print("\n🧑‍⚖️ Examiner Feedback:\n", feedback, flush=True)

        # ============================================
        # ✅ Case Picker Logic (No input)
        # ============================================

        def select_case_from_folder():
            print("📁 Selecting case from folder...", flush=True)
            BASE_FOLDER = "history_based/general_medicine/cases/chest_pain"
            search_term = "herpes_zoster_002"

            try:
                matching_cases = [f[:-5] for f in os.listdir(BASE_FOLDER)
                                  if f.endswith(".json") and search_term in f.lower()]
                if not matching_cases:
                    print("❌ No matching cases found.", flush=True)
                    return None

                selected_name = matching_cases[0]
                case = get_case_by_name(BASE_FOLDER, selected_name)

                if isinstance(case, dict):
                    print(
                        f"✅ Case selected: {case.get('case_id')}", flush=True)
                    return case
                else:
                    print("❌ Case loaded but not a dict.", flush=True)
                    return None

            except Exception as e:
                print("🔥 Exception during case loading:", e, flush=True)
                return None

        # ============================================
        # ✅ Launch Entry
        # ============================================

        print("🚀 [START] history_runner.py", flush=True)
        selected_case = select_case_from_folder()
        if selected_case:
            asyncio.run(run_history_station(selected_case))
        else:
            print("❌ No case selected. Exiting.", flush=True)

    except Exception:
        print("❌ Unhandled Exception occurred:")
        traceback.print_exc()


if __name__ == "__main__":
    safe_main()
