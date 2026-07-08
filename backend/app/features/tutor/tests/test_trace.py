"""Unit tests for the per-agent input/output capture."""

from app.features.tutor.graph import trace


def test_capture_records_agents():
    trace.start_capture()
    trace.record("diagnostic", {"system": "sys-d", "user": "usr-d"}, "obs")
    trace.record("hint", {"system": "sys-h", "user": "usr-h"}, "a hint")

    result = trace.build_dict()
    assert set(result) == {"diagnostic", "hint"}
    assert result["diagnostic"] == {
        "input": {"system": "sys-d", "user": "usr-d"},
        "output": "obs",
    }
    assert result["hint"]["output"] == "a hint"


def test_repeated_agent_becomes_list():
    trace.start_capture()
    trace.record("hint", {"system": "s", "user": "u1"}, "hint 1")
    trace.record("hint", {"system": "s", "user": "u2"}, "hint 2")

    result = trace.build_dict()
    assert isinstance(result["hint"], list)
    assert [entry["output"] for entry in result["hint"]] == ["hint 1", "hint 2"]


def test_record_without_capture_is_noop():
    # No start_capture() -> recording is a no-op and build_dict is empty.
    trace._capture.set(None)
    trace.record("diagnostic", {"system": "s", "user": "u"}, "x")
    assert trace.build_dict() == {}
