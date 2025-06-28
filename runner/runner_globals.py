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
    # ============================================
    # 🔁 STEP 1: Clear all keys in PATIENT_MEMORY
    # If a value is boolean → reset to False
    # Otherwise (str, dict, etc.) → reset to None
    # ============================================
    for key in PATIENT_MEMORY:
        if isinstance(PATIENT_MEMORY[key], bool):
            PATIENT_MEMORY[key] = False
        else:
            PATIENT_MEMORY[key] = None

    # ============================================
    # 🧠 STEP 2: Reinitialize essential memory fields
    # These fields must always exist with defaults
    # ============================================

    # Used to store fallback LLM short-term memory
    PATIENT_MEMORY["llm_fallback_memory"] = {}

    # Stores the last AI response so it’s not repeated
    PATIENT_MEMORY["last_response"] = ""

    # Resets mood to neutral at the start of the case
    PATIENT_MEMORY["patient_mood"] = "neutral"

    # ============================================
    # 🚦 STEP 3: Reset phase-related status flags
    # Used in transition and fallback logic
    # ============================================

    # Has the diagnosis been explained to the doctor yet?
    PATIENT_MEMORY["diagnosis_explained"] = False

    # Timestamp for when transition phase started
    PATIENT_MEMORY["transition_started_at"] = None

    # Tracks if LLM fallback logic has been triggered
    PATIENT_MEMORY["ai_fallback_triggered"] = False

