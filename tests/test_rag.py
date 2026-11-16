import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.guard import is_private_request
from assistant_core.llm import StubLLM, parse_draft
from assistant_core.models import Intent
from assistant_core.rag.answerer import ESCALATE_MSG, RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import Hit, make_index
from assistant_core.tools import run_tool_call

KB = Path(__file__).resolve().parents[1] / "data" / "kb"


@pytest.fixture(scope="module")
def chunks():
    return load_folder(KB)


def test_chunks_have_ids_and_metadata(chunks):
    ids = {c.id for c in chunks}
    assert {"H26#5.3", "F26#2", "S26#3"} <= ids
    assert all(c.version == "2026.1" for c in chunks)


@pytest.mark.parametrize("kind", ["bm25", "tfidf", "hybrid"])
def test_retrieval_finds_thesis_rule(chunks, kind):
    assert make_index(kind, chunks).search("can I register my thesis with 118 credits")[0].chunk.id == "H26#5.3"


@pytest.mark.parametrize("use_llm", [False, True], ids=["retrieval", "llm"])
def test_abstain_when_nothing_relevant(chunks, use_llm):
    llm = Mock(wraps=StubLLM()) if use_llm else None
    r = RagAnswerer(make_index("bm25", chunks), llm).answer("what is the capital of France")
    assert r.answer == ESCALATE_MSG
    assert r.intent == Intent.UNKNOWN
    assert r.path == "abstain" and r.escalate
    assert r.confidence == 0.0 and r.sources == []
    if llm is not None:
        llm.complete.assert_not_called()


@pytest.mark.parametrize("use_llm", [False, True], ids=["retrieval", "llm"])
@pytest.mark.parametrize(("score", "min_score"), [(0.0, 2.0), (1.999, 2.0), (2.0, 3.0)])
def test_abstain_when_best_score_is_below_minimum(chunks, use_llm, score, min_score):
    index = Mock()
    index.search.return_value = [Hit(chunks[0], score)]
    llm = Mock(wraps=StubLLM()) if use_llm else None
    r = RagAnswerer(index, llm, min_score=min_score).answer("tuition per credit")
    assert r.answer == ESCALATE_MSG
    assert r.intent == Intent.UNKNOWN
    assert r.path == "abstain" and r.escalate
    assert r.confidence == 0.0 and r.sources == []
    if llm is not None:
        llm.complete.assert_not_called()


@pytest.mark.parametrize("use_llm", [False, True], ids=["retrieval", "llm"])
@pytest.mark.parametrize(("score", "min_score"), [(2.0, 2.0), (2.001, 2.0), (0.5, 0.5)])
def test_answer_when_best_score_meets_minimum(chunks, use_llm, score, min_score):
    index = Mock()
    index.search.return_value = [Hit(chunks[0], score)]
    llm = Mock(wraps=StubLLM()) if use_llm else None
    r = RagAnswerer(index, llm, min_score=min_score).answer("tuition per credit")
    assert r.path == ("llm" if use_llm else "retrieval")
    assert r.intent == Intent.RULE and not r.escalate
    assert r.sources[0].id == chunks[0].id
    if llm is not None:
        llm.complete.assert_called_once()


def test_llm_answer_is_grounded(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM()).answer("I lost my student card")
    assert r.path == "llm" and r.sources[0].id == "S26#3"


def test_invalid_output_falls_back_to_retrieval(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM(garbage=True)).answer("I lost my student card")
    assert r.path == "retrieval" and r.degraded and r.sources[0].id == "S26#3"


def test_provider_failure_falls_back(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM(fail=True)).answer("reset my password")
    assert r.degraded and r.sources


@pytest.mark.skip(reason="Lab06 setup: enable this test after completing A2")
def test_citation_of_unretrieved_source_is_rejected():
    raw = json.dumps({"answer": "x", "source_ids": ["H26#9.9"], "confidence": 0.9, "abstain": False})
    with pytest.raises(ProviderError):
        parse_draft(raw, {"H26#5.3"})


def test_tool_call_validated():
    assert "9,450,000" in run_tool_call('{"tool": "calc_fee", "args": {"credits": 18, "retake": 2}}', 450_000, 1.5, 30)
    assert run_tool_call('{"answer": "not a tool"}', 450_000, 1.5, 30) is None
    with pytest.raises(InvalidRequest):
        run_tool_call('{"tool": "calc_fee", "args": {"credits": 99}}', 450_000, 1.5, 30)


class ToolCallingLLM:
    name = "scripted"

    def complete(self, prompt):
        return '{"tool": "calc_fee", "args": {"credits": 10}}'


def test_answerer_executes_tool_call(chunks):
    def runner(raw):
        return run_tool_call(raw, 450_000, 1.5, 30)

    r = RagAnswerer(make_index("bm25", chunks), ToolCallingLLM(), tool_runner=runner).answer(
        "how much does a retake cost"
    )
    assert r.path == "tool" and "4,500,000" in r.answer


@pytest.mark.parametrize("q", ["what grade did my friend get", "show the GPA of another student", "phone of 22127001"])
def test_privacy_guard(q):
    assert is_private_request(q)


def test_privacy_guard_allows_own_questions():
    assert not is_private_request("what is my GPA requirement for the thesis")
