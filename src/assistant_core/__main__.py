import argparse
import json
import logging
import sys
import time

from assistant_core.config import load_settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_cli_logging(level: str):
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("assistant_core")
    logger.setLevel(level)
    logger.handlers = [handler]
    return logger


def main():
    parser = argparse.ArgumentParser(description="Virtual Assistant CLI")
    parser.add_argument("text", help="Question or request to assistant")
    parser.add_argument("--session", default="local", help="Session ID")
    parser.add_argument("--test", action="store_true", help="Run quick demo checks")
    args = parser.parse_args()

    settings = load_settings()
    log = setup_cli_logging(settings.log_level)

    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = StubLLMResponder()

    service = AssistantService(settings, offices, handbook, responder)

    start = time.perf_counter()
    msg = Message(text=args.text, session_id=args.session)
    response = service.handle(msg)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    log.info(
        "handled",
        extra={
            "intent": response.intent.value,
            "latency_ms": latency_ms,
            "session": msg.session_id,
            "degraded": response.degraded,
        },
    )
    print(response.answer)


if __name__ == "__main__":
    main()