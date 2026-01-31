from collections import Counter

def reason(tickets, logs, merchants):
    reasoning = {}

    # Pattern 1: Missing Webhooks → Checkout blank
    webhook_issues = [
        t for t in tickets if t["error"] == "Missing webhook"
    ]

    # Pattern 2: API Unauthorized → API keys not updated
    api_issues = [
        t for t in tickets if "401 API Unauthorized" in t["error"]
    ]

    # Pattern 3: Frontend not deployed
    frontend_issues = [
        t for t in tickets if "Frontend build not deployed" in t["error"]
    ]

    # Pattern 4: Env variables missing
    env_issues = [
        t for t in tickets if "environment variables" in t["error"]
    ]

    if len(webhook_issues) >= 2:
        reasoning["root_cause"] = "Multiple merchants missing webhook configuration after migration"
        reasoning["confidence"] = 0.92

    elif len(api_issues) >= 2:
        reasoning["root_cause"] = "API keys not updated for several merchants after migration"
        reasoning["confidence"] = 0.9

    elif len(frontend_issues) >= 2:
        reasoning["root_cause"] = "Frontend not deployed properly for multiple merchants"
        reasoning["confidence"] = 0.88

    elif len(env_issues) >= 1:
        reasoning["root_cause"] = "Environment variables not set during migration"
        reasoning["confidence"] = 0.85

    else:
        reasoning["root_cause"] = "No strong pattern detected yet"
        reasoning["confidence"] = 0.4

    return reasoning
