import argparse
import logging
import time

from assistant_core.config import load_settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


def main() -> None:
    parser = argparse.ArgumentParser(description="Virtual Assistant CLI")
    parser.add_argument("text", help="Question or request to assistant")
    parser.add_argument("--session", default="local", help="Session ID")
    args = parser.parse_args()

    settings = load_settings()
    setup_logging(settings.log_level)
    log = logging.getLogger("assistant_core")

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
