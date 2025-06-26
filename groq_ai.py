# ============================================
# ✅ Imports and Setup
# ============================================

from runner_globals import PATIENT_MEMORY
import os
import re
import json
import random
import asyncio
import requests
from PIL import Image
from typing import Dict
from dotenv import load_dotenv
from difflib import SequenceMatcher

from openai import OpenAI  # Optional: used for client init if needed
from feedback import track_question
from mood_manager import update_memory_with_mood
from runner_globals import PATIENT_MEMORY, SESSION_LOG, reset_patient_memory

# ============================================
# ✅ Load API Key from .env
# ============================================

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in environment. Please check your .env file.")

# ============================================
# ✅ Optional: Initialize OpenAI Client
# (Only if you plan to use it later)
# ============================================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# ============================================
# ✅ Function: Generate LLM Reply from Groq API
# ============================================


def generate_reply(prompt: str) -> str:
    """Send prompt to Groq API and return the model's response."""
    url = "https://api.groq.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, json=body, headers=headers)

    try:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("⚠️ Error getting LLM reply:", e)
        return "Sorry, I’m not sure how to respond to that right now."

# ============================================
# ✅ Image Display for Examination
# ============================================


def show_examination_image(case_folder: str, case_name: str):
    try:
        possible_names = [
            f"{case_name}.jpg",
            f"{case_name}.png",
            "shingles.jpg",
            "default_exam.jpg"
        ]
        for filename in possible_names:
            image_path = os.path.join(case_folder, filename)
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.show()
                print(f"🖼️ Showing image: {image_path}")
                return
        print("❌ No image found for examination.")
    except Exception as e:
        print("⚠️ Error displaying image:", e)

# ============================================
# ✅ Helper Functions
# ============================================


def clean_response(text: str) -> str:
    if not isinstance(text, str):
        return "Sorry doctor, I didn’t understand that."
    text = re.sub(r"\*.*?\*", "", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(
        r"\b(sighs|gulps|pauses|panting|gasps|uh|um|mmm)[^\.!?]*[\.!?]?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b([A-Za-z])-([A-Za-z]+)\b", r"\2", text)
    text = re.sub(r'\b(\w+)(\s+\1){1,}', r'\1', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    if text.endswith(("and", "but", ",")):
        text += "..."
    if "call me doctor" in text.lower() or "i'm your doctor" in text.lower():
        return "Sorry, I didn’t mean that. I’m just a patient feeling unwell."
    return text


def call_llm(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system",
                    "content": "You are a UKMLA patient. Answer realistically."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.6,
            max_tokens=57
        )
        return clean_response(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"⚠️ LLM Fallback Failed: {e}")
        return "Sorry doctor, I’m not sure how to answer that."

# ============================================
# ✅ Family History Risk Factor Logic
# ============================================


def get_family_history_reply(station_id: str, station_type: str, diagnosis: str) -> str:
    try:
        if station_type == "counselling":
            return f"My {random.choice(['mother', 'father'])} also had {diagnosis}."
        path = os.path.join("risk_factors", f"{station_id}.json")
        with open(path, "r") as f:
            data = json.load(f)
        relevant = data.get("family_relevant", [])
        distractors = data.get("family_distractors", [])
        pool = []
        if random.random() < 0.7 and relevant:
            pool.append(random.choice(relevant))
        if distractors:
            pool.append(random.choice(distractors))
        return random.choice(pool) if pool else "Not sure about family history, doctor."
    except Exception as e:
        print(f"⚠️ Family history load error: {e}")
        return "Not sure about family history, doctor."

# ============================================
# ✅ Patient Reply Generator
# ============================================


# ============================================
# ✅ IMPORTS
# ============================================


# ============================================
# ✅ LLM CALL FUNCTION (GROQ)
# ============================================


def generate_reply(prompt: str) -> str:
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system",
                    "content": "You are a simulated patient in a UKMLA OSCE exam."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 200
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        # ✅ Safe access
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()

        print("⚠️ Unexpected LLM response (no 'choices'):\n", result)
        return "Sorry, I’m not sure how to respond to that right now."

    except Exception as e:
        print("⚠️ Exception in generate_reply():", e)
        return "Sorry, I’m not sure how to respond to that right now."


# ============================================
# ✅ PATIENT RESPONSE GENERATOR
# ============================================

def get_patient_reply(user_input: str, case: dict, current_phase: str) -> str:
    from runner_globals import PATIENT_MEMORY
    from groq_ai import generate_reply  # Replace with your actual model caller

    name = case.get("name", "The patient")
    age = case.get("age", "40")
    symptoms_list = case.get("symptoms", [])
    patient_mood = PATIENT_MEMORY.get("patient_mood", "neutral")

    presenting_complaint = case.get("presenting_complaint", "some symptoms")

    social_history = case.get("social_history", {})
    family_history = case.get("family_history", [])

    prompt = f"""
You are {name}, a {age}-year-old UKMLA OSCE patient.
“If the doctor already acknowledged a symptom or reassured you, don’t mention that again unless re-asked.”

You ONLY experience these symptoms: {symptoms_list}.
Your current mood is: {patient_mood}.
Your main concern today is: {presenting_complaint}.
❗️If you've already said a symptom, do NOT repeat it unless doctor specifically re-asks. Each reply should move forward in context.


🧠 HOW TO RESPOND:
- Respond NATURALLY and BRIEFLY, like a real human — avoid robotic or overly formal tone.
- Mention only ONE vague symptom early on, like "discomfort" or "weird feeling".
- ❌ Avoid buzzwords like 'burning pain', 'dermatomal rash', or 'radiating pain' unless the doctor specifically asks.
- NEVER list all symptoms or red flags at once.
- Reveal more ONLY if the doctor asks clearly and specifically.
- NEVER give medical advice or diagnosis guesses.
- Do NOT mention unrelated symptoms like dizziness or breathlessness unless they exist in your symptom list.

🚫 SOCIAL & FAMILY HISTORY RULE:
- ❗️Do NOT mention social or family history unless directly asked by the doctor.
- If asked:
  • Smoking → "{social_history.get('smoking', 'N/A')}"
  • Alcohol → "{social_history.get('alcohol', 'N/A')}"
  • Diet → "{social_history.get('diet', 'N/A')}"
  • Exercise → "{social_history.get('exercise', 'N/A')}"
  • Family history → "{', '.join(family_history) or 'None relevant'}"

🎯 SCENARIO:
The doctor asked: "{user_input}"

🎭 Match your mood: {patient_mood}. Sound real, brief, and natural — as someone concerned about: {presenting_complaint}

🎤 Now respond as the patient:
"""

    try:
        response = generate_reply(prompt)

        if isinstance(response, str):
            return response.strip()

        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content.strip()

        print("⚠️ Warning: LLM response missing 'choices'")
        return "Sorry, I’m not sure how to respond to that right now."

    except Exception as e:
        print(f"⚠️ Error getting LLM reply: {e}")
        return "Sorry, I’m not sure how to respond to that right now."


# ============================================
# ✅ Async Wrapper (Non-blocking AI)
# ============================================

async def get_patient_reply_async(doctor_input, case, current_phase):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_patient_reply, doctor_input, case, current_phase)


# ============================================
# ✅ Examiner Feedback Generator
# ============================================

def generate_examiner_comment(session_log, case):
    try:
        prompt = f"""
You are a UKMLA OSCE examiner providing structured and professional feedback.

=========================
🧾 CASE DETAILS:
- Station: {case['station_name']}
- Diagnosis: {case['diagnosis']}
- Presenting Complaint: {case['presenting_complaint']}
- Symptoms: {", ".join(case.get('symptoms', []))}
- Red Flags: {", ".join(case.get('red_flags', []))}
- Differentials: {", ".join(case.get('differentials', []))}
- PMH: {", ".join(case.get('medical_history', []))}
- Medications: {", ".join(case.get('medications', []))}
- Family History: {", ".join(case.get('family_history', []))}
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
# ============================================
# ✅ Phase Prompt Adjuster (Optional Utility)
# ============================================


def adjust_prompt_for_phase(phase, doctor_input):
    """Adjusts doctor input based on the current OSCE phase."""
    if phase == "ice":
        return f"Doctor is exploring your ICE concerns. {doctor_input}"
    elif phase == "management":
        return f"Doctor is discussing management. {doctor_input}"
    elif phase == "transition":
        return f"Doctor is reviewing findings and explaining them. {doctor_input}"
    return doctor_input
