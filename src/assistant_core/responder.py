"""Response generation interface and implementations."""

from typing import Protocol

from assistant_core.errors import ProviderError
from assistant_core.knowledge import Rule


class Responder(Protocol):
    """Interface for response generators."""

    def explain(self, question: str, rule: Rule) -> str:
        ...


class TemplateResponder:
    """Generate a response without using an AI provider."""

    def explain(self, question: str, rule: Rule,) -> str:
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Simulate an LLM provider."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError(
                "stub provider unavailable"
            )

        return (
            f"Based on '{rule.title}': {rule.text}"
        )