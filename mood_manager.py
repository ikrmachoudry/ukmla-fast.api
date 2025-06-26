# ============================================
# ✅ FILE: mood_manager.py
# PURPOSE: Dynamically manage patient emotional tone based on doctor input, memory & repetition
# ============================================

from difflib import SequenceMatcher
from runner_globals import PATIENT_MEMORY, SESSION_LOG

# ============================================
# ✅ Similarity Helper
# ============================================


def is_similar_question(new_q: str, old_q: str) -> bool:
    return SequenceMatcher(None, new_q.strip().lower(), old_q.strip().lower()).ratio() > 0.85

# ============================================
# ✅ Mood Detection Based on Keywords
# ============================================


def detect_mood(user_input: str, memory: dict) -> str:
    user_input_lower = user_input.lower()
    current_mood = memory.get("patient_mood", "neutral")

    if any(kw in user_input_lower for kw in ["cancer", "surgery", "serious condition", "tumor", "operation"]):
        return "shocked"

    if any(kw in user_input_lower for kw in [
        "take your time", "i understand", "i'm here to help", "you'll be okay", "don't worry"
    ]):
        return "comforted"

    if any(kw in user_input_lower for kw in [
        "why didn’t you", "you should have", "didn’t you say earlier", "you never mentioned"
    ]):
        return "defensive"

    if any(kw in user_input_lower for kw in [
        "nothing serious", "it’s okay", "benign", "good news", "you’ll recover"
    ]):
        return "relieved"

    if any(kw in user_input_lower for kw in [
        "worried", "concerned", "alarming", "very serious", "emergency"
    ]):
        return "anxious"

    return current_mood

# ============================================
# ✅ Main Mood Update Function
# ============================================


def update_memory_with_mood(user_input: str, memory: dict) -> None:
    user_input_lower = user_input.strip().lower()
    repeat_count = 0

    # --- Check for repeated questions
    for past_q in SESSION_LOG.get("questions", []):
        if is_similar_question(user_input_lower, past_q):
            repeat_count += 1

    if repeat_count >= 1 and user_input not in SESSION_LOG["duplicate_questions"]:
        SESSION_LOG["duplicate_questions"].append(user_input)

    # --- Mood escalation by repetition
    if repeat_count == 1:
        new_mood = "mildly_annoyed"
    elif repeat_count == 2:
        new_mood = "frustrated"
    elif repeat_count >= 3:
        new_mood = "angry"
    else:
        new_mood = detect_mood(user_input, memory)

    memory["patient_mood"] = new_mood

    # --- Handle repeated asking of name
    if "name" in user_input_lower:
        memory["name_asked_count"] = memory.get("name_asked_count", 0) + 1
        if memory["name_asked_count"] >= 3:
            memory["patient_mood"] = "frustrated"
        elif memory["name_asked_count"] == 2:
            memory["patient_mood"] = "mildly_annoyed"
