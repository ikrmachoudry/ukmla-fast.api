import os
import json
from PIL import Image
import glob

# ✅ Base folders
CASE_FOLDER = "history_based/general_medicine/cases/chest_pain"
MEDIA_FOLDER = "media"

# ✅ Load JSON case


def load_case(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ Exam findings


def get_case_findings(case: dict) -> str:
    findings = []
    vitals = case.get("examination", {}).get("vitals", {})
    if vitals:
        findings.append("📊 VITAL SIGNS:")
        for key, value in vitals.items():
            findings.append(f"  • {key}: {value}")

    for key, label in {
        "gpe": "General Appearance",
        "skin_exam": "Skin Exam",
        "cardio_exam": "Cardiovascular Exam",
        "resp_exam": "Respiratory Exam"
    }.items():
        value = case.get("examination", {}).get(key)
        if value:
            findings.append(f"🩺 {label}: {value}")

    return "\n".join(findings)

# ✅ Investigation results


def get_investigation_results(case: dict) -> str:
    return f"🧪 INVESTIGATIONS:\n{case.get('investigation_findings', 'No results available.')}"

# ✅ Image Viewer (robust to case & extension differences)


def show_case_image(case: dict, case_filename: str):
    image_key = case.get("exam_image", "")
    if not image_key:
        print("❌ No 'exam_image' field found.")
        return

    # Normalize path (convert to Unix-style and lower-case for matching)
    base_name = os.path.splitext(os.path.basename(image_key))[0].lower()

    # Search recursively in media folder
    pattern = os.path.join(MEDIA_FOLDER, "**", "*")
    all_files = glob.glob(pattern, recursive=True)

    for f in all_files:
        if os.path.isfile(f):
            fname = os.path.splitext(os.path.basename(f))[0].lower()
            if fname == base_name:
                print(f"\n🖼️ Showing exam image: {f}")
                Image.open(f).show()
                return

    print(f"❌ Could not find matching image for: {image_key}")


# ✅ MAIN
if __name__ == "__main__":
    print("🔍 Available cases:")
    cases = [f for f in os.listdir(CASE_FOLDER) if f.endswith(".json")]
    for idx, case_file in enumerate(cases, 1):
        print(f"{idx}. {case_file[:-5]}")

    selected_index = int(input("👉 Select case number: ")) - 1
    selected_file = cases[selected_index]
    case_path = os.path.join(CASE_FOLDER, selected_file)

    print(f"\n✅ Loaded: {selected_file[:-5]}")
    case = load_case(case_path)

    # ✅ Display findings
    print("\n📋 Examination Findings:\n")
    print(get_case_findings(case))

    # ✅ Display investigation results
    print("\n🧾 Investigation Results:\n")
    print(get_investigation_results(case))

    # ✅ Show image
    show_case_image(case, selected_file)
