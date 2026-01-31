from collections import Counter

def reason(tickets, logs, merchants):
    reasoning = {}

    error_list = [t["error"] for t in tickets]
    error_count = Counter(error_list)

    reasoning["analysis"] = []

    for error, count in error_count.items():
        if "Missing webhook" in error:
            reasoning["analysis"].append(
                ("Webhook misconfiguration across merchants", count)
            )

        elif "401 API Unauthorized" in error:
            reasoning["analysis"].append(
                ("API keys not updated after migration", count)
            )

        elif "Frontend build not deployed" in error:
            reasoning["analysis"].append(
                ("Frontend not deployed for merchants", count)
            )

        elif "environment variables" in error:
            reasoning["analysis"].append(
                ("Environment variables not set", count)
            )

    # Sort by most affected
    reasoning["analysis"].sort(key=lambda x: x[1], reverse=True)

    top_issue = reasoning["analysis"][0]

    reasoning["root_cause"] = top_issue[0]
    reasoning["affected_merchants"] = top_issue[1]
    reasoning["confidence"] = round(0.85 + (top_issue[1] * 0.02), 2)

    return reasoning
