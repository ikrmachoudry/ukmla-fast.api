# ============================================
# 🤖 GROQ LLM PATIENT MODULE
# Handles AI replies as UKMLA patient + feedback generation
# ============================================

import os
import json
import random
import re
import asyncio
import requests
from dotenv import load_dotenv
from runner.runner_globals import PATIENT_MEMORY, SESSION_LOG


# ============================================
# 🔑 Load API Key
# ============================================

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ============================================
# 🧠 Clean Up Model Response
# ============================================

def clean_response(text: str) -> str:
    if not isinstance(text, str):
        return "Sorry doctor, I didn’t understand that."
    text = re.sub(r"\*.*?\*", "", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\b(sighs|gulps|uh|um)[^\.!?]*[\.!?]?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b([A-Za-z])-([A-Za-z]+)\b", r"\2", text)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

# ============================================
# 🗣️ Core LLM Function
# ============================================

def generate_reply(prompt: str, model: str = "llama3-70b-8192") -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a simulated patient in a UKMLA OSCE exam."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 300
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return clean_response(content)
    except Exception as e:
        print(f"⚠️ generate_reply error: {e}")
        return "Sorry doctor, I’m not sure how to respond to that."

# ============================================
# 🧬 FAMILY HISTORY LOGIC
# ============================================

def get_family_history_reply(station_id: str, diagnosis: str, station_type="history") -> str:
    try:
        if station_type == "counselling":
            return f"My {random.choice(['mother', 'father'])} also had {diagnosis}."
        path = os.path.join("data", "risk_factors", f"{station_id}.json")
        with open(path, "r") as f:
            data = json.load(f)
        relevant = data.get("family_relevant", [])
        distractors = data.get("family_distractors", [])
        options = relevant + distractors
        return random.choice(options) if options else "Not sure about family history, doctor."
    except Exception as e:
        print(f"⚠️ Family history load error: {e}")
        return "Not sure about family history, doctor."

# ============================================
# 👨‍⚕️ PATIENT REPLY GENERATOR
# ============================================

def get_patient_reply(user_input: str, case: dict, phase: str) -> str:
    name = case.get("name", "the patient")
    age = case.get("age", "40")
    symptoms = case.get("symptoms", [])
    mood = PATIENT_MEMORY.get("patient_mood", "neutral")
    concern = case.get("presenting_complaint", "some issue")

    social = case.get("social_history", {})
    family = case.get("family_history", [])

    prompt = f"""
You are {name}, a {age}-year-old UKMLA patient.
Your symptoms are: {symptoms}
Your mood is: {mood}
Your concern today is: {concern}

Do not repeat previously said symptoms unless asked again.

Respond naturally and briefly:
- Avoid complex medical terms unless doctor uses them
- Reveal only 1 symptom per doctor question
- Don’t list red flags unless clearly asked

Only mention:
• Smoking: {social.get('smoking', 'N/A')}
• Alcohol: {social.get('alcohol', 'N/A')}
• Diet: {social.get('diet', 'N/A')}
• Exercise: {social.get('exercise', 'N/A')}
• Family History: {', '.join(family) or 'None known'}

🧑‍⚕️ Doctor said: “{user_input}”
Now reply as the patient:
"""
    return generate_reply(prompt)

# ============================================
# ⚡️ Async Version for FastAPI
# ============================================

async def get_patient_reply_async(user_input, case, phase):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_patient_reply, user_input, case, phase)

# ============================================
# 📝 EXAMINER FEEDBACK GENERATOR
# ============================================

def generate_examiner_comment(log: dict, case: dict) -> str:
    try:
        prompt = f"""
You are a UKMLA examiner. Provide structured feedback.

CASE: {case.get('station_name', 'unknown')}
DIAGNOSIS: {case.get('diagnosis')}
SYMPTOMS: {case.get('symptoms')}
RED FLAGS: {case.get('red_flags')}
ICE: {case.get('ice')}
PMH: {case.get('medical_history')}
FHx: {case.get('family_history')}
SHx: {case.get('social_history')}

QUESTIONS: {log.get('questions')}
DUPLICATES: {log.get('duplicate_questions')}
TAGS: {log.get('question_tags')}

Return your feedback in 7 points:
1. Summary
2. Score (/10)
3. Missed Questions
4. Differential Clarity
5. Risk Factors
6. Safety Netting
7. Improvement Tip
"""
        return generate_reply(prompt)
    except Exception as e:
        print("⚠️ Examiner feedback failed:", e)
        return "⚠️ Feedback unavailable."
