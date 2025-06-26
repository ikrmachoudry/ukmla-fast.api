# ============================================
# ✅ FILE: patient_concerns.py
# PURPOSE: Manage common and condition-specific patient concerns
# ============================================

common_concerns = {
    "basic": {
        "what_happening": "Doctor, what exactly is happening to me?",
        "treatment_plan": "How are you going to treat me?",
        "serious": "Is it serious or life-threatening?",
        "recovery_time": "How long will it take to recover fully?",
        "work_return": "When can I go back to work?",
        "next_steps": "What are you going to do now?"
    },
    "chest_pain": {
        "lifestyle": "Will I have to change my diet or lifestyle now?",
        "exercise": "Can I still do exercise after this?"
    }
}


def get_unasked_concerns(case_type: str, answered_keywords: set) -> dict:
    """
    Returns a dict of patient concerns that were not yet addressed.

    Parameters:
    - case_type: e.g. "chest_pain"
    - answered_keywords: a set of already covered concern keys

    Returns:
    - A dictionary of remaining concerns
    """
    # Start with basic concerns
    all_concerns = dict(common_concerns.get("basic", {}))

    # Merge in case-specific concerns
    case_specific = common_concerns.get(case_type.lower(), {})
    all_concerns.update(case_specific)

    # Filter out answered concerns
    remaining = {
        key: concern for key, concern in all_concerns.items()
        if key not in answered_keywords
    }

    return remaining
