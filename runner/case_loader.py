# ============================================
# 📦 CASE LOADER MODULE for UKMLA STATION
# Loads a single case JSON based on name, level, and category
# Called by runners like history_runner.py, counselling_runner.py etc.
# ============================================

import os
import json

# ============================================
# 🧠 OPTIONAL: Enrich case with extra fields (e.g., symptoms)
# ============================================


def enrich_case(case):
    """
    Adds fallback symptoms based on diagnosis keyword if missing.
    Optional helper that can be expanded later.
    """
    diagnosis = case.get("diagnosis", "").lower()

    if "myocardial infarction" in diagnosis or "heart attack" in diagnosis:
        case.setdefault("symptoms", [
            "exertional chest pain",
            "radiates to left arm",
            "relieved by rest",
            "sweating",
            "shortness of breath",
            "nausea"
        ])
    return case

# ============================================
# 📁 CASE PATH RESOLVER
# ============================================


def resolve_case_path(case_name: str, level: str, category: str = "history_based") -> str:
    """
    Constructs file path for given case based on your project structure.

    Args:
        case_name (str): e.g. "chest_pain"
        level (str): e.g. "b"
        category (str): e.g. "history_based", "counselling_based"

    Returns:
        str: Full file path to the .json case
    """
    file_name = f"{case_name}_{level}.json"
    return os.path.join("data", category, case_name, file_name)

# ============================================
# 📖 CASE LOADER MAIN FUNCTION
# ============================================


def load_case(case_name: str, level: str, category: str = "history_based") -> dict | None:
    """
    Loads and parses the JSON case file based on given parameters.

    Args:
        case_name (str): e.g. "chest_pain"
        level (str): e.g. "b"
        category (str): Folder like "history_based"

    Returns:
        dict: Parsed case dictionary (enriched if needed), or None if error
    """
    case_path = resolve_case_path(case_name, level, category)

    try:
        with open(case_path, 'r', encoding='utf-8') as f:
            case_data = json.load(f)
        case_data = enrich_case(case_data)
        case_data["file_path"] = case_path  # Optional tracking
        return case_data
    except Exception as e:
        print(f"❌ Error loading case {case_name}: {e}")
        return None
# ============================================
# 🔍 Load Case by Fuzzy Match (ID or station)
# ============================================


def load_case_by_keyword(keyword: str, base_dir="data/history_based") -> dict | None:
    """
    Finds and loads a case JSON file by matching keyword in case_id or station_name.
    Accepts partial, lowercase matches.
    """
    keyword = keyword.strip().lower()

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        case_data = json.load(f)
                        case_id = case_data.get("case_id", "").lower()
                        station = case_data.get("station_name", "").lower()
                        if keyword in case_id or keyword in station:
                            case_data["file_path"] = full_path
                            return enrich_case(case_data)
                except Exception as e:
                    print(f"⚠️ Error loading file {file}: {e}")
    return None


def load_case_by_keyword(keyword: str, base_path="data/history_based") -> dict | None:
    """
    Searches all cases in history_based for a keyword match in filename or case_id.
    Supports partial keywords like '002', 'herpes', 'mi'.

    Returns:
        dict or None
    """
    keyword = keyword.strip().lower()

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                try:
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        case = json.load(f)

                    file_match = keyword in file.lower()
                    id_match = keyword in case.get("case_id", "").lower()
                    name_match = keyword in case.get(
                        "station_name", "").lower()
                    diag_match = keyword in case.get("diagnosis", "").lower()

                    if file_match or id_match or name_match or diag_match:
                        case["file_path"] = path
                        return case
                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")
                    continue
    return None
