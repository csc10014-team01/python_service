from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, Office, OfficeDirectory, Rule
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


@pytest.fixture
def mock_settings():


@pytest.fixture
def mock_settings():
    return Settings(
        data_dir=Path("data"),
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
        llm_provider="stub",
    )


@pytest.fixture
def mock_offices():
    data = {
        "training": Office(name="Training Office", room="A.101", hours="08:00-17:00"),
        "library": Office(name="Library", room="B.201", hours="07:00-20:00"),
    }
    return OfficeDirectory(data)


@pytest.fixture
def mock_handbook():
    rules = [
        Rule(
            id="H26-1",
            title="Thesis Registration",
            text="Students need at least 100 credits to register for thesis.",
            keywords=["thesis", "registration", "credits"],
        )
    ]
    return Handbook(rules)


@pytest.fixture
def service(mock_settings, mock_offices, mock_handbook):
    responder = StubLLMResponder()
    return AssistantService(mock_settings, mock_offices, mock_handbook, responder)