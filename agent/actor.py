def act(action, reasoning):
    print("\n===== AGENT ANALYSIS REPORT =====\n")

    print("Issues Detected Across System:")
    for issue, count in reasoning["analysis"]:
        print(f"- {issue} → {count} merchants affected")

    print("\nPrimary Root Cause Chosen :", reasoning["root_cause"])
    print("Confidence Level          :", reasoning["confidence"])
    print("Proposed Action           :", action)
    print("Status                    : Awaiting human approval")

    print("\n=================================\n")
