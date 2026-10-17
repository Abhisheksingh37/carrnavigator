from graph import create_profile, skill_gap, missing_prereqs

create_profile("Test", "AI Engineer", {"Python": 3, "Git": 3})

gaps = skill_gap("Test")
for g in gaps:
    print(g["skill"], "| have:", g["have"], "| needed:", g["needed"])
    print("   missing prereqs:", [p["prerequisite"] for p in missing_prereqs("Test", g["skill"])])