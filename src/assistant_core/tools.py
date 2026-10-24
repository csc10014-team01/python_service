import re

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    retake_match = re.search(r"(\d+)\s*retake", text.lower())
    numbers = [int(number) for number in re.findall(r"\d+", text)]

    retake_credits = int(retake_match.group(1)) if retake_match else 0

    other_numbers = numbers.copy()

    if retake_match:
        other_numbers.remove(retake_credits)

    if not other_numbers:
        raise InvalidRequest("How many credits?")

    return other_numbers[0], retake_credits


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")

    return int(credits * rate + retake * rate * retake_multiplier)
