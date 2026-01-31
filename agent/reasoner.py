from collections import Counter

def reason(state):
    tickets = state.observations["tickets"]
    error_counts = Counter(t["error"] for t in tickets)

    hypotheses = []

    for error, count in error_counts.items():
        if "Missing webhook" in error:
            hypotheses.append({
                "cause": "Webhook misconfiguration",
                "confidence": min(0.7 + count * 0.05, 0.95),
                "risk": "Low",
                "blast_radius": "Medium"
            })
        elif "401 API Unauthorized" in error:
            hypotheses.append({
                "cause": "API keys not rotated",
                "confidence": min(0.7 + count * 0.05, 0.95),
                "risk": "Medium",
                "blast_radius": "High"
            })
        elif "Frontend build not deployed" in error:
            hypotheses.append({
                "cause": "Frontend not deployed",
                "confidence": min(0.65 + count * 0.05, 0.9),
                "risk": "Low",
                "blast_radius": "Low"
            })
        elif "environment variables" in error:
            hypotheses.append({
                "cause": "Environment variables missing",
                "confidence": min(0.65 + count * 0.05, 0.9),
                "risk": "Medium",
                "blast_radius": "Medium"
            })

    hypotheses.sort(key=lambda x: x["confidence"], reverse=True)
    state.hypotheses = hypotheses
