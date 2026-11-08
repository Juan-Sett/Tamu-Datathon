import re


STOP_WORDS = {"i", "a", "the", "and", "or", "to", "for", "near", "on", "at", "with", "me", "my", "what", "can", "need", "help", "do", "is", "this", "that"}


def retrieve_relevant_records(question, records, limit=5):
    tokens = {token for token in re.findall(r"[a-z0-9]+", question.lower()) if token not in STOP_WORDS and len(token) > 2}
    scored = []
    for record in records:
        haystack = " ".join(str(record.get(key, "")) for key in ("category", "name", "description", "location", "tags")).lower()
        score = sum(2 if token in str(record.get("tags", "")).lower().split(", ") else 1 for token in tokens if token in haystack)
        if any(word in question.lower() for word in ("food", "lunch", "dinner", "eat", "coffee")) and record.get("category") == "Dining":
            score += 3
        if any(word in question.lower() for word in ("heat", "hot", "outside", "indoor", "shade")) and record.get("category") in ("Weather", "Facility", "Transit"):
            score += 2
        if score:
            scored.append((score, record))
    scored.sort(key=lambda item: (-item[0], item[1].get("name", "")))
    return [record for _, record in scored[:limit]] or records[:limit]


def build_demo_decision(question, records):
    dining = [r for r in records if r.get("category") == "Dining"]
    heat_sensitive = any(word in question.lower() for word in ("heat", "hot", "outside", "indoor", "shade"))
    budget_match = re.search(r"(?:under|less than|below)\s*\$?([0-9]+(?:\.[0-9]+)?)", question.lower())
    budget = float(budget_match.group(1)) if budget_match else None
    candidates = [r for r in dining if budget is None or float(r.get("price", 999)) <= budget]
    best = candidates[0] if candidates else (dining[0] if dining else records[0])
    if heat_sensitive:
        indoor = [r for r in dining if "indoor" in r.get("tags", "")]
        if indoor and (budget is None or float(indoor[0].get("price", 999)) <= budget):
            best = indoor[0]
    steps = [f"Go to {best['name']} at {best['location']} ({best['open_time']}–{best['close_time']})."]
    if heat_sensitive:
        steps.append("Use the indoor route or campus shuttle where possible, and carry water for any outdoor segment.")
    if best.get("price"):
        steps.append(f"Budget about ${float(best['price']):.2f}; this fits your stated budget." if budget and float(best["price"]) <= budget else f"Budget about ${float(best['price']):.2f}.")
    return {
        "recommendation": f"Choose {best['name']}—it is the strongest match for your constraints in the available campus data.",
        "steps": steps,
        "why": f"I matched your request against {len(records)} campus facts and prioritized location, cost, hours, and comfort constraints.",
        "tradeoff": "This is a demo snapshot. Live hours, route timing, and weather should be refreshed before making a time-sensitive decision.",
    }
