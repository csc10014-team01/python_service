import json
import re

from pydantic import BaseModel, Field, ValidationError

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


class FeeArgs(BaseModel):
    credits: int = Field(ge=1, le=30)
    retake: int = Field(default=0, ge=0, le=30)


TOOL_SPECS = {
    "calc_fee": {
        "description": "Compute tuition in VND for a number of credits and retake credits.",
        "parameters": FeeArgs.model_json_schema(),
    },
}


def run_tool_call(raw: str, rate: int, retake_multiplier: float, max_credits: int) -> str | None:
    """Validate a model's tool request and compute the result with the fee calculator."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "tool" not in data:
        return None
    if data["tool"] != "calc_fee":
        raise InvalidRequest(f"unknown tool {data['tool']!r}")
    try:
        args = FeeArgs.model_validate(data.get("args", {}))
    except ValidationError as exc:
        raise InvalidRequest("invalid tool arguments") from exc
    total = tuition(args.credits, args.retake, rate, retake_multiplier, max_credits)
    return f"Your tuition is {total:,} VND."
