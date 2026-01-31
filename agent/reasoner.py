from collections import Counter

def reason(tickets, logs, merchants):
    issues = [t["issue"] for t in tickets]
    issue_count = Counter(issues)

    errors = [l["error"] for l in logs]
    error_count = Counter(errors)

    reasoning = {}

    if issue_count["Checkout failing after migration"] > 1 and error_count["checkout_api_500"] > 1:
        reasoning["root_cause"] = "Possible platform regression in checkout API after migration"
        reasoning["confidence"] = 0.85

    elif issue_count["Webhook not triggering"] > 0:
        reasoning["root_cause"] = "Merchant webhook misconfiguration"
        reasoning["confidence"] = 0.65

    else:
        reasoning["root_cause"] = "Unknown"
        reasoning["confidence"] = 0.3

    return reasoning
