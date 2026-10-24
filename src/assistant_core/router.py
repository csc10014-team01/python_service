from assistant_core.models import Intent


def route(text: str, office_names: set[str] | None = None) -> Intent:
    t = text.lower()
    if any(w in t for w in ["hi", "hello", "hey"]):
        return Intent.GREETING
    if any(w in t for w in ["tuition", "fee", "credits", "retake"]):
        return Intent.FEE
    if office_names and any(name in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
