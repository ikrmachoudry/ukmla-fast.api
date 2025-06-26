import traceback
import sys
import os
from case_loader import get_case_by_name

# ✅ Global debug handler to force traceback


def force_traceback():
    try:
        raise Exception("🛠️ Forced exception to test traceback")
    except:
        traceback.print_exc()


# ✅ Debug paths
BASE_FOLDER = "history_based/general_medicine/cases/chest_pain"
CASE_NAME = "herpes_zoster_002"

print("🔍 STEP 1: Checking case file path...", flush=True)

full_path = os.path.join(BASE_FOLDER, CASE_NAME + ".json")
print("📄 Full path to JSON:", full_path, flush=True)

if not os.path.exists(full_path):
    print("❌ File NOT FOUND at path above.", flush=True)
    force_traceback()
    sys.exit(1)

print("✅ File exists. Trying to load using get_case_by_name()", flush=True)

try:
    case = get_case_by_name(BASE_FOLDER, CASE_NAME)
    if case is None:
        print("❌ Returned None! Likely failed to load or parse JSON", flush=True)
        force_traceback()
    else:
        print("✅ JSON loaded successfully!", flush=True)
        print("🧾 ID:", case.get("case_id"))
        print("📋 Station:", case.get("station_name"))
except Exception as e:
    print("🛑 CRASH while loading case:")
    traceback.print_exc()
