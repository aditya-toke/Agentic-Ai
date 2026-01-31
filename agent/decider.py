def decide(reasoning):
    cause = reasoning["root_cause"]

    if "webhook" in cause.lower():
        return "Send webhook setup guide to affected merchants and update documentation"

    elif "api keys" in cause.lower():
        return "Notify merchants to regenerate API keys and alert support team"

    elif "frontend" in cause.lower():
        return "Ask merchants to redeploy frontend and provide deployment checklist"

    elif "environment variables" in cause.lower():
        return "Send environment variable setup instructions"

    else:
        return "Monitor for more signals before acting"
