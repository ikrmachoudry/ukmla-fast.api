from tabulate import tabulate


def print_chest_pain_revision_table():
    print("\n📊 Chest Pain Differential Diagnosis Revision Table:\n")

    data = [
        ["MI (STEMI/NSTEMI)", "Crushing pain, radiates to arm/jaw, >20 mins",
         "ST↑ (STEMI), T↓ (NSTEMI), ↑Troponin", "MONA, PCI/thrombolysis"],
        ["Unstable Angina", "Pain at rest/minimal exertion, no troponin rise",
            "Normal ECG, normal troponin", "Anti-anginals, admit"],
        ["Stable Angina", "Exertional pain, relieved by rest or GTN <5min",
            "Normal ECG or ST depression on stress", "GTN, BB, statin, lifestyle"],
        ["Aortic Dissection", "Tearing pain to back, pulse/BP difference",
            "Widened mediastinum, CT angio", "Labetalol, urgent surgery"],
        ["Pulmonary Embolism", "Pleuritic pain, dyspnea, hemoptysis",
            "S1Q3T3, ↑D-dimer, CTPA", "LMWH/DOAC, oxygen, thrombolysis"],
        ["Pericarditis", "Sharp pain, better sitting up",
            "ST↑ all leads, PR↓, pericardial rub", "NSAIDs + Colchicine"],
        ["GERD", "Burning after meals/lying, bitter taste",
            "Normal exam, possible endoscopy", "PPI, lifestyle change"],
        ["Costochondritis", "Localized rib pain, reproducible",
            "Tender chest wall, normal ECG", "NSAIDs, reassurance"],
        ["Herpes Zoster", "Burning dermatomal pain, rash after 1–3 days",
            "Vesicular rash, no cardiac signs", "Acyclovir <72h, analgesia"],
        ["MSK Chest Pain", "Post-strain, movement reproduces pain",
            "Localized tender spot, normal vitals", "NSAIDs, rest"],
        ["Anxiety/Panic", "Chest tightness, tingling, fear of dying",
            "Hyperventilation, normal ECG", "CBT, breathing techniques"]
    ]

    headers = ["Condition", "Key Differentiators",
               "Investigations", "Management"]
    print(tabulate(data, headers=headers, tablefmt="grid"))
