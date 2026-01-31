def act(action, reasoning):
    print("\n--- AGENT ACTION ---")
    print("Reason:", reasoning["root_cause"])
    print("Confidence:", reasoning["confidence"])
    print("Proposed Action:", action)
    print("Awaiting human approval...\n")
