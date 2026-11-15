"""Configuration contract tests, isolated from the developer's environment."""

import traceback
from pathlib import Path

import pytest

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in (
        "ASSISTANT_DATA_DIR",
        "LLM_PROVIDER",
        "LLM_API_KEY",
        "LLM_TIMEOUT_S",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "KB_DIR",
        "RETRIEVAL_KIND",
        "RETRIEVAL_MIN_SCORE",
        "PROMPT_VERSION",
        "CREDIT_RATE_VND",
        "RETAKE_MULTIPLIER",
        "MAX_CREDITS",
        "LOG_LEVEL",
        "API_ADMIN_KEY",
        "WEATHER_URL",
        "WEATHER_TIMEOUT_S",
        "CAMPUS_LAT",
        "CAMPUS_LON",
        "RATE_LIMIT_PER_MIN",
        "DATABASE_URL",
        "SESSION_SALT",
    ):
        monkeypatch.delenv(name, raising=False)


def test_defaults_work_without_api_key():
    settings = load_settings(env_file=None)
    assert settings == Settings()
    assert settings.data_dir == Path("data")
    assert settings.llm_provider == "stub"
    assert settings.llm_api_key is None
    assert settings.credit_rate_vnd == 450_000
    assert settings.retake_multiplier == 1.5
    assert settings.max_credits == 30
    assert settings.log_level == "INFO"


def test_reads_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "ASSISTANT_DATA_DIR=custom-data\n"
        "LLM_PROVIDER=example-provider\n"
        "LLM_API_KEY=test-only-key\n"
        "CREDIT_RATE_VND=500000\n"
        "RETAKE_MULTIPLIER=2\n"
        "MAX_CREDITS=24\n"
        "LOG_LEVEL=debug\n",
        encoding="utf-8",
    )
    settings = load_settings(env_file)
    assert settings.data_dir == Path("custom-data")
    assert settings.llm_provider == "example-provider"
    assert settings.llm_api_key == "test-only-key"
    assert settings.credit_rate_vnd == 500_000
    assert settings.retake_multiplier == 2.0
    assert settings.max_credits == 24
    assert settings.log_level == "DEBUG"


def test_environment_takes_precedence_over_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("CREDIT_RATE_VND=500000\nLLM_API_KEY=file-key\n", encoding="utf-8")
    monkeypatch.setenv("CREDIT_RATE_VND", "600000")
    monkeypatch.setenv("LLM_API_KEY", "environment-key")
    settings = load_settings(env_file)
    assert settings.credit_rate_vnd == 600_000
    assert settings.llm_api_key == "environment-key"


def test_none_disables_dotenv_loading(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("MAX_CREDITS=10\n", encoding="utf-8")
    assert load_settings(env_file=None).max_credits == 30


def test_loads_default_dotenv_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("MAX_CREDITS=20\n", encoding="utf-8")
    assert load_settings().max_credits == 20


def test_missing_dotenv_is_optional(tmp_path):
    assert load_settings(tmp_path / "missing.env") == Settings()


@pytest.mark.parametrize("key", [None, "", "   "])
def test_openai_provider_requires_api_key(monkeypatch, key):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    if key is not None:
        monkeypatch.setenv("LLM_API_KEY", key)
    with pytest.raises(ConfigError, match="LLM_API_KEY is required"):
        load_settings(env_file=None)


@pytest.mark.parametrize("provider", ["stub", "template", "ollama"])
def test_local_providers_work_without_api_key(monkeypatch, provider):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    settings = load_settings(env_file=None)
    assert settings.llm_provider == provider
    assert settings.llm_api_key is None


def test_loads_rag_configuration_from_environment(monkeypatch):
    monkeypatch.setenv("KB_DIR", "custom-kb")
    monkeypatch.setenv("RETRIEVAL_KIND", "tfidf")
    monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.2")
    monkeypatch.setenv("LLM_TIMEOUT_S", "12")
    monkeypatch.setenv("LLM_MODEL", "custom-model")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("PROMPT_VERSION", "answer_v2")
    settings = load_settings(env_file=None)
    assert settings.kb_dir == Path("custom-kb")
    assert settings.retrieval_kind == "tfidf"
    assert settings.retrieval_min_score == 0.2
    assert settings.llm_timeout_s == 12
    assert settings.llm_model == "custom-model"
    assert settings.llm_base_url == "http://localhost:11434"
    assert settings.prompt_version == "answer_v2"


def test_api_key_is_hidden_from_settings_representation(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-only-secret")
    settings = load_settings(env_file=None)
    assert "test-only-secret" not in repr(settings)
    assert "test-only-secret" not in str(settings)


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("CREDIT_RATE_VND", "not-a-number"),
        ("CREDIT_RATE_VND", "0"),
        ("CREDIT_RATE_VND", "-1"),
        ("RETAKE_MULTIPLIER", "invalid"),
        ("RETAKE_MULTIPLIER", "0"),
        ("RETAKE_MULTIPLIER", "-1"),
        ("RETAKE_MULTIPLIER", "nan"),
        ("RETAKE_MULTIPLIER", "inf"),
        ("MAX_CREDITS", "1.5"),
        ("MAX_CREDITS", "0"),
        ("MAX_CREDITS", "-1"),
        ("LOG_LEVEL", "INVALID"),
        ("LLM_PROVIDER", "   "),
    ],
)
def test_invalid_configuration_raises_config_error(monkeypatch, variable, value):
    monkeypatch.setenv(variable, value)
    with pytest.raises(ConfigError):
        load_settings(env_file=None)


def test_config_error_traceback_does_not_reveal_environment_values(monkeypatch):
    secret = "test-only-secret"
    monkeypatch.setenv("LLM_API_KEY", secret)
    monkeypatch.setenv("CREDIT_RATE_VND", secret)
    with pytest.raises(ConfigError) as error:
        load_settings(env_file=None)
    assert secret not in "".join(traceback.format_exception(error.type, error.value, error.tb))


def test_example_environment_is_valid():
    env_file = Path(__file__).resolve().parents[1] / ".env.example"
    assert load_settings(env_file) == Settings()
