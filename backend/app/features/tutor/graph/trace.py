"""Per-request capture of each agent's LLM input and output.

A lightweight, in-process alternative to LangSmith for seeing exactly what each
agent received and produced. `graph/llm.complete()` records every call; the service
starts a capture before running the graph and reads the result back as a dict:

    {
      "diagnostic": {"input": {"system": "...", "user": "..."}, "output": "..."},
      "hint":       {"input": {...}, "output": "..."},
      ...
    }

An agent called more than once in a turn (e.g. a regenerated hint) becomes a list.
Uses a ContextVar so concurrent requests never mix their captures.
"""

import contextvars

_capture: contextvars.ContextVar[list | None] = contextvars.ContextVar(
    "agent_io_capture", default=None
)


def start_capture() -> None:
    """Begin capturing agent I/O for the current request/task."""
    _capture.set([])


def record(agent: str, prompt: dict, output: str) -> None:
    """Record one agent LLM call (no-op if capture isn't active)."""
    buffer = _capture.get()
    if buffer is not None:
        buffer.append({"agent": agent, "input": prompt, "output": output})


def build_dict() -> dict:
    """Return the captured calls as {agent_name: {input, output}} (list if repeated)."""
    buffer = _capture.get() or []
    result: dict = {}
    for rec in buffer:
        name = rec["agent"]
        entry = {"input": rec["input"], "output": rec["output"]}
        if name not in result:
            result[name] = entry
        else:
            if not isinstance(result[name], list):
                result[name] = [result[name]]
            result[name].append(entry)
    return result
