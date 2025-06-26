# ============================================
# 📦 CASE LOADER MODULE for UKMLA STATION
# Handles loading, enriching, and path management for case files
# ============================================

import os
import json

# ============================================
# 🧠 CASE ENRICHER: Auto-fill fields if missing
# ============================================


def enrich_case(case):
    """
    Optional: Add auto-generated symptoms or fields based on diagnosis
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
# 🔁 BULK CASE LOADER (Recursively loads .jsons)
# ============================================


def load_all_cases(base_path="history_based"):
    """
    Recursively loads all .json case files from base_path and its subfolders.
    Adds 'category' and 'sub_category' from folder structure.
    """
    all_cases = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                try:
                    file_path = os.path.join(root, file)

                    with open(file_path, "r", encoding="utf-8") as f:
                        case_data = json.load(f)

                    # Extract folder structure to label categories
                    path_parts = os.path.normpath(root).split(os.sep)
                    category = path_parts[-3] if len(
                        path_parts) >= 3 else "unknown"
                    sub_category = path_parts[-1] if len(
                        path_parts) >= 1 else "unknown"

                    # Add metadata
                    case_data.setdefault("category", category)
                    case_data.setdefault("sub_category", sub_category)
                    case_data["file_path"] = file_path

                    # Optionally enrich
                    case_data = enrich_case(case_data)
                    all_cases.append(case_data)

                except Exception as e:
                    print(f"❌ Error loading {file_path}: {e}")

    return all_cases

# ============================================
# 📁 SINGLE CASE PATH RESOLVER
# ============================================


def get_case_by_name(folder, name):
    path = os.path.join(folder, name + ".json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)  # ✅ Properly parse to dict
    except Exception as e:
        print("❌ Error loading JSON:", e)
        return None

# ============================================
# 📖 CASE LOADER FROM FILE
# ============================================


def load_case(path):
    """
    Loads and parses a JSON case file given full path.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading case from {path}: {e}")
        return None

# ============================================
# 🧠 INTERACTIVE CASE PICKER
# ============================================


def select_case_interactively(base_path="history_based"):
    """
    Lets user choose a case interactively from all loaded case files.
    """
    all_cases = load_all_cases(base_path)
    print(f"🔍 DEBUG: Loaded {len(all_cases)} cases from {base_path}")

    if not all_cases:
        print("❌ No cases found.")
        return None

    print("\n📋 Available Cases:\n")
    for i, case in enumerate(all_cases):
        name = case.get("station_name", "Unnamed")
        case_id = case.get("case_id", "unknown")
        print(f"{i+1}. {case_id} — {name}")

    try:
        choice = int(input("\n🔍 Enter the number of the case to run: ")) - 1
        return all_cases[choice]["file_path"] if 0 <= choice < len(all_cases) else None
    except (ValueError, IndexError):
        print("❌ Invalid choice.")
        return None

# ============================================
# 🧪 TEST MODE: View all loaded cases (Run directly)
# ============================================


if __name__ == "__main__":
    print("🔁 Testing case loader...")
    cases = load_all_cases()
    print(f"✅ Total cases found: {len(cases)}")
    for i, case in enumerate(cases):
        print(
            f"{i+1}. {case.get('case_id')} — {case.get('station_name')} → {case.get('file_path')}")
