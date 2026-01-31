def act(action, reasoning):
    print("\n===== AGENT ACTION REPORT =====")
    print("Root Cause Identified :", reasoning["root_cause"])
    print("Confidence Level      :", reasoning["confidence"])
    print("Proposed Action       :", action)
    print("Status                : Awaiting human approval")
    print("================================\n")
