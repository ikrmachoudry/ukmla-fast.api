# ============================================
# ✅ FILE: feedback.py
# PURPOSE: Track doctor questions and generate report
# ============================================

import requests
import os
from core.runner_globals import SESSION_LOG

FEEDBACK_LOG = {
    "data_gathering": set(),
    "interpersonal": set(),
    "management": set(),
    "repetitions": 0,
    "asked_questions": set()
}


def track_question(doctor_input: str):
    """Classify question by domain and track repetition."""
    text = doctor_input.lower()

    if doctor_input in FEEDBACK_LOG["asked_questions"]:
        FEEDBACK_LOG["repetitions"] += 1
    else:
        FEEDBACK_LOG["asked_questions"].add(doctor_input)

    # 🧠 Data Gathering
    if any(k in text for k in ["pain", "duration", "radiate", "severity", "trigger", "location"]):
        FEEDBACK_LOG["data_gathering"].add("symptom_analysis")
    if "medication" in text or "drugs" in text:
        FEEDBACK_LOG["data_gathering"].add("medications")
    if "allerg" in text:
        FEEDBACK_LOG["data_gathering"].add("allergies")
    if "family" in text:
        FEEDBACK_LOG["data_gathering"].add("family_history")

    # 💬 ICE (Ideas, Concerns, Expectations)
    if any(k in text for k in ["what do you think", "your idea", "what's causing", "what's going on"]):
        FEEDBACK_LOG["interpersonal"].add("idea")
    if any(k in text for k in ["are you worried", "any concerns", "bother you", "worried about"]):
        FEEDBACK_LOG["interpersonal"].add("concern")
    if any(k in text for k in ["what do you expect", "what are you hoping", "would you like"]):
        FEEDBACK_LOG["interpersonal"].add("expectation")

    # 💊 Management
    if any(k in text for k in ["admit", "admission", "hospital", "stay in"]):
        FEEDBACK_LOG["management"].add("admission")
    if any(k in text for k in ["treatment", "medication", "painkiller", "aspirin", "spray"]):
        FEEDBACK_LOG["management"].add("treatment")
    if any(k in text for k in ["follow-up", "gp", "review", "see you again"]):
        FEEDBACK_LOG["management"].add("followup")
    if any(k in text for k in ["safety", "red flag", "come back", "warning sign"]):
        FEEDBACK_LOG["management"].add("safety_netting")


def generate_report(case_id: str):
    print(f"\n\n🧾 Patient Station Report – {case_id}\n")

    print("✅ You asked about:")
    if "symptom_analysis" in FEEDBACK_LOG["data_gathering"]:
        print("🧠 Chest pain, onset, radiation, severity, triggers")
    if "family_history" in FEEDBACK_LOG["data_gathering"]:
        print("👨‍👩‍👧‍👦 Family history of heart disease")
    if "medications" in FEEDBACK_LOG["data_gathering"]:
        print("💊 Medications")
    if "allergies" in FEEDBACK_LOG["data_gathering"]:
        print("🌿 Allergies")

    if "idea" in FEEDBACK_LOG["interpersonal"]:
        print("🫀 ICE: 'What do you think is causing this?'")
    if "concern" in FEEDBACK_LOG["interpersonal"]:
        print("😟 ICE: 'Are you worried about anything?'")
    if "expectation" in FEEDBACK_LOG["interpersonal"]:
        print("💬 ICE: 'What were you hoping we’d do?'")

    print("\n❌ You missed:")
    if "allergies" not in FEEDBACK_LOG["data_gathering"]:
        print("🚫 Allergies")
    if "expectation" not in FEEDBACK_LOG["interpersonal"]:
        print("🚫 Asking about patient’s expectation")
    if "safety_netting" not in FEEDBACK_LOG["management"]:
        print("🚫 Safety-netting question")

    print("\n🧠 Performance Summary")
    print("Data Gathering:", "✅ Strong" if len(
        FEEDBACK_LOG["data_gathering"]) >= 3 else "⚠️ Incomplete")
    print("Interpersonal:", "✅ All ICE covered" if len(
        FEEDBACK_LOG["interpersonal"]) >= 2 else "⚠️ Missed some ICE")
    print("Management:", "✅ Clear plan" if len(
        FEEDBACK_LOG["management"]) >= 2 else "⚠️ Management lacking")
    print("Listening:", "✅ No repetition" if FEEDBACK_LOG["repetitions"]
          == 0 else f"❌ Repeated {FEEDBACK_LOG['repetitions']} question(s)")

    print("\n📘 Tip: Review missed areas before the next station!\n")


def generate_examiner_comment(session_log, case):
    try:
        prompt = f"""
You are a UKMLA OSCE examiner providing structured and professional feedback.

=========================
🧾 CASE DETAILS:
- Station: {case.get('station_name', 'N/A')}
- Diagnosis: {case.get('diagnosis', 'N/A')}
- Presenting Complaint: {case.get('presenting_complaint', 'N/A')}
- Symptoms: {', '.join(case.get('symptoms', []))}
- Red Flags: {', '.join(case.get('red_flags', []))}
- Differentials: {', '.join(case.get('differentials', []))}
- PMH: {', '.join(case.get('medical_history', []))}
- Medications: {', '.join(case.get('medications', []))}
- Family History: {', '.join(case.get('family_history', []))}
- Social History: Smoking: {case['social_history'].get('smoking', 'N/A')}, Alcohol: {case['social_history'].get('alcohol', 'N/A')}, Diet: {case['social_history'].get('diet', 'N/A')}, Exercise: {case['social_history'].get('exercise', 'N/A')}
- ICE: Ideas: {case['ice'].get('ideas', '')} | Concerns: {case['ice'].get('concerns', '')} | Expectations: {case['ice'].get('expectations', '')}
- Exam Findings: {case.get('exam_findings', 'N/A')}
- Investigation Findings: {case.get('investigation_findings', 'N/A')}
=========================

💬 QUESTIONS: {session_log['questions']}
🔁 DUPLICATES: {session_log['duplicate_questions']}
📊 DOMAIN TAGS: Data: {session_log['question_tags']['data_gathering']} | Interpersonal: {session_log['question_tags']['interpersonal']} | Management: {session_log['question_tags']['management']}

Give feedback under these headings:
1. Summary (max 3 lines)
2. Score (/10)
3. Missed Key Questions
4. Differential Diagnoses
5. Safety Netting
6. Risk Factors
7. Management Plan
8. Investigations
9. One Improvement Suggestion
"""

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a senior UKMLA OSCE examiner giving structured feedback."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 800
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip().replace("**", "")

    except Exception as e:
        print(f"⚠️ Examiner Feedback Error: {e}")
        return "⚠️ AI Feedback could not be generated. Please try again later."
