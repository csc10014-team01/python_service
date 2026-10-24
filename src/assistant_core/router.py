from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})


def route(text: str, office_names: set[str]) -> Intent:
    """Classify a user question using simple rules."""
    normalized = text.lower().strip().rstrip("?!.")

    if normalized in GREETINGS:
        return Intent.GREETING

    if "fee" in normalized or "tuition" in normalized:
        return Intent.FEE

    if any(name in normalized for name in office_names):
        return Intent.OFFICE

    return Intent.RULE
