"""Prompt templates for each tutor agent.

One module per LLM-backed agent, each exposing its SYSTEM prompt(s) and a small
function that renders the USER prompt from the current turn's state. Keeping the
prompts here (out of the node logic) makes them easy to read, diff, and tune
without touching control flow.

The wording of every SYSTEM / USER prompt is intentionally preserved verbatim —
JSON output is enforced separately by `graph.llm.run_agent` (via each agent's
Pydantic response schema in `graph.schemas`), not by editing these prompts.
"""
