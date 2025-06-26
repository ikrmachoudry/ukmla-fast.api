# --- FILE: runner_globals.py
# ✅ Centralized memory + session log

PATIENT_MEMORY = {
    "presenting_complaint": None,
    "pain_history": None,
    "family_history_father": None,
    "family_history_mother": None,
    "family_history": None,
    "past_medical_history": None,
    "past_episode": None,
    "allergies": None,
    "medications": None,
    "smoking_alcohol": None,
    "diet": None,
    "exercise": None,
    "social": None,
    "identity": None,
    "reassurance": None,
    "management_explained": False,
    "diagnosis_acknowledged": False,
    "concern_asked": False,
    "llm_fallback_memory": {},
    "last_response": "",
    "patient_mood": "neutral",

    # ✅ NEW for advanced flow handling
    "diagnosis_explained": False,       # 👈 True once student explains diagnosis
    "transition_started_at": None,      # 👈 Timestamp when transition begins
    "ai_fallback_triggered": False      # 👈 Prevent double fallback responses
}

SESSION_LOG = {
    "questions": [],
    "duplicate_questions": [],
    "question_tags": {
        "data_gathering": [],
        "management": [],
        "interpersonal": []
    }
}


def reset_patient_memory():
    for key in PATIENT_MEMORY:
        if isinstance(PATIENT_MEMORY[key], bool):
            PATIENT_MEMORY[key] = False
        else:
            PATIENT_MEMORY[key] = None

    PATIENT_MEMORY["llm_fallback_memory"] = {}
    PATIENT_MEMORY["last_response"] = ""
    PATIENT_MEMORY["patient_mood"] = "neutral"

    # ✅ Reset new transition/fallback flags
    PATIENT_MEMORY["diagnosis_explained"] = False
    PATIENT_MEMORY["transition_started_at"] = None
    PATIENT_MEMORY["ai_fallback_triggered"] = False
