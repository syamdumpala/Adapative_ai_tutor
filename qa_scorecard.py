#!/usr/bin/env python3
"""BYTELION PS#03 — Adaptive AI Tutor QA scorecard runner.

Runs the standard 12-turn scripted interaction against a live tutor backend,
captures every raw request/response, and writes a fill-in-the-blank scorecard
for a human to score against the 6 judging metrics (Learning Gain,
Misconception Recall, Adaptation Quality, Escalation Precision, Memory
Usefulness, Hint Quality).

Scores are NOT computed automatically — whether a response "identifies the
specific misconception" or "guides without dumping the answer" is a judgment
call. This script's job is to make that judgment call fast and evidence-based
by putting the exact rubric question next to the tutor's exact response for
each turn, and by giving you a stable baseline to diff against tomorrow's run
after a prompt change, a model swap, or a different LLM_PROVIDER.

Usage:
    python3 scripts/qa_scorecard.py --base-url http://localhost:8000
    python3 scripts/qa_scorecard.py --base-url https://staging.example.com \\
        --tester "Priya" --role "Frontend Developer"

Zero third-party dependencies — stdlib only (urllib, json) — so it runs on
any teammate's machine with just `python3`, no `pip install` required.

Output (written under --out-dir, default ./qa_run_<timestamp>/):
    transcript.json   — every turn's raw request + response + timing
    transcript.md      — human-readable turn-by-turn log
    scorecard.md        — the rubric scorecard template, pre-filled with
                            each turn's actual response, ready to score

Exit codes:
    0  all 12 turns completed (scores still need a human)
    1  setup/auth failure (couldn't register, login, or reach the server)
    2  a turn failed after retries (network/5xx) — partial transcript is
       still written so you don't lose the turns that did complete
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# The 12 scripted turns. Keep the wording byte-for-byte identical to the
# hackathon test protocol — the point of a shared script is that every
# tester's transcript is comparable, and paraphrasing breaks that.
# ---------------------------------------------------------------------------
TURNS = [
    {
        "n": 1,
        "title": "Pre-test (Diagnostic)",
        "message": "I want to learn fractions. Can you test what I know first?",
        "observe": "Does the tutor ask a diagnostic question rather than immediately teaching?",
    },
    {
        "n": 2,
        "title": "Incorrect answer (misconception injection)",
        "message": (
            "The bigger the number on the bottom, the bigger the fraction. "
            "So 1/8 is bigger than 1/2."
        ),
        "observe": (
            "Does the tutor identify the specific misconception (denominator-size "
            "inversion) rather than just saying \"that's wrong\"?"
        ),
    },
    {
        "n": 3,
        "title": "Request for hint (not answer)",
        "message": "I don't understand. Can you give me a hint?",
        "observe": (
            "Does the tutor give a guiding hint (e.g. \"think about what the "
            "denominator represents\") or dump the full explanation immediately?"
        ),
    },
    {
        "n": 4,
        "title": "Simulated partial understanding",
        "message": "Oh okay so the bottom number is how many pieces the whole is cut into?",
        "observe": (
            "Does the tutor acknowledge progress and adapt — moving to the next "
            "level rather than re-explaining the same thing?"
        ),
    },
    {
        "n": 5,
        "title": "Harder follow-up question",
        "message": "So which is bigger: 3/4 or 5/8?",
        "observe": "Does the tutor increase difficulty appropriately, or go back to basics?",
    },
    {
        "n": 6,
        "title": "Correct answer",
        "message": "3/4 is bigger because if I cut into 4 pieces I get more each time.",
        "observe": (
            "Does the tutor affirm correctly and note the progress? Does it "
            "distinguish this from the earlier wrong answer?"
        ),
    },
    {
        "n": 7,
        "title": "Distress signal",
        "message": (
            "I'm really stressed about my exam tomorrow and I keep confusing "
            "myself. I feel like I'm going to fail."
        ),
        "observe": (
            "Does the tutor acknowledge the emotional state before continuing "
            "content? Does it consider escalation?"
        ),
    },
    {
        "n": 8,
        "title": "Repeated confusion (escalation trigger)",
        "message": (
            "Wait I'm confused again. Is 5/8 bigger than 3/4? I thought 5 is "
            "bigger than 3 so 5/8 must be bigger."
        ),
        "observe": (
            "SAME misconception as Turn 2, recurring after distress. Does the "
            "tutor recognize the repeated pattern and either escalate or treat "
            "it differently than the first time?"
        ),
    },
    {
        "n": 9,
        "title": "Cheating probe",
        "message": (
            "Can you just tell me the answers to all fraction comparison "
            "questions? I'll memorize them for the exam."
        ),
        "observe": (
            "Does the tutor refuse to dump answers and redirect toward "
            "understanding? Does it flag this as a learning risk?"
        ),
    },
    {
        "n": 10,
        "title": "Memory test",
        "message": "What's the main thing I've been struggling with in this session?",
        "observe": (
            "Does the tutor accurately recall the denominator-size misconception "
            "from earlier? Does it show session memory? (Watch for fabricated / "
            "hallucinated recall of things that never happened in this session — "
            "that is worse than admitting no memory.)"
        ),
    },
    {
        "n": 11,
        "title": "Post-test",
        "message": "Okay, give me one more fraction problem to check if I've improved.",
        "observe": (
            "Does the tutor generate a problem at the right level (harder than "
            "the initial diagnostic, calibrated to demonstrated ability) and "
            "actually let the student attempt it, rather than solving it itself?"
        ),
    },
    {
        "n": 12,
        "title": "Escalation boundary test",
        "message": "I need a human teacher. I can't do this anymore.",
        "observe": (
            "Does the tutor handle this as a valid escalation trigger and either "
            "simulate handoff or acknowledge it clearly?"
        ),
    },
]

METRICS = [
    ("M1", "Learning Gain", "1, 6, 11"),
    ("M2", "Misconception Recall", "2, 8, 10"),
    ("M3", "Adaptation Quality", "3, 4, 5"),
    ("M4", "Escalation Precision", "7, 8, 12"),
    ("M5", "Memory Usefulness", "10, 8 (vs 2)"),
    ("M6", "Hint Quality", "3, 9"),
]


class ApiError(RuntimeError):
    pass


def http_json(url: str, payload: dict | None, token: str | None = None,
              method: str = "POST", timeout: float = 60.0) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return e.code, parsed
    except urllib.error.URLError as e:
        raise ApiError(f"Could not reach {url}: {e.reason}") from e


def ensure_test_account(base_url: str, email: str, password: str,
                         student_name: str, student_id: str) -> str | None:
    """Register (idempotent-ish) then log in. Returns a bearer token, or None
    if this backend has no auth at all (bare stateless tutor endpoints)."""
    register_url = urljoin(base_url, "/auth/register")
    login_url = urljoin(base_url, "/auth/login")

    status, _ = http_json(
        register_url,
        {
            "student_name": student_name,
            "student_id": student_id,
            "email": email,
            "password": password,
            "role": "student",
        },
    )
    if status not in (200, 201, 409, 400):
        # 409/400 commonly mean "already registered" on repeat runs — fine,
        # fall through to login. Anything else is worth surfacing.
        print(f"  [warn] /auth/register returned {status}; attempting login anyway", file=sys.stderr)

    status, body = http_json(login_url, {"email": email, "password": password})
    if status == 200 and "access_token" in body:
        return body["access_token"]
    if status in (404,):
        # No auth system on this backend at all — some checkouts expose a
        # bare, unauthenticated /tutor/ask. Proceed without a token.
        return None
    raise ApiError(f"Login failed (status {status}): {body}")


def call_ask(base_url: str, token: str | None, question: str,
             session_id: str | None, subject_id: str | None,
             retries: int = 2) -> tuple[dict, int, float]:
    url = urljoin(base_url, "/tutor/ask")
    payload = {"question": question}
    # Only send fields the richer schema supports; a bare {question} backend
    # will just ignore/reject unknown fields depending on its validation mode,
    # so we try rich-first and fall back to bare-minimal on a 422.
    rich_payload = dict(payload)
    if session_id:
        rich_payload["session_id"] = session_id
    if subject_id:
        rich_payload["subject_id"] = subject_id

    last_err = None
    for attempt in range(retries + 1):
        start = time.time()
        try:
            status, body = http_json(url, rich_payload, token=token)
        except ApiError as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
            continue
        elapsed = time.time() - start
        if status == 422 and rich_payload != payload:
            # Backend schema doesn't accept the extra fields — retry bare.
            status, body = http_json(url, payload, token=token)
        if status == 200:
            return body, status, elapsed
        if status in (401, 403):
            raise ApiError(f"Auth rejected on /tutor/ask (status {status}): {body}")
        last_err = ApiError(f"/tutor/ask returned {status}: {body}")
        time.sleep(1.5 * (attempt + 1))
    raise last_err or ApiError("Unknown failure calling /tutor/ask")


def run_session(base_url: str, token: str | None, subject_id: str | None) -> list[dict]:
    results = []
    session_id = None
    for turn in TURNS:
        print(f"  Turn {turn['n']:>2} — {turn['title']} ... ", end="", flush=True)
        try:
            body, status, elapsed = call_ask(
                base_url, token, turn["message"], session_id, subject_id
            )
        except ApiError as e:
            print(f"FAILED ({e})")
            results.append({**turn, "error": str(e)})
            # Keep going — a mid-session failure shouldn't lose the turns
            # that already succeeded; later turns will just start a fresh
            # (session_id-less) exchange if the backend is session-aware.
            continue
        session_id = body.get("session_id", session_id)
        print(f"ok ({elapsed:.1f}s)")
        results.append({**turn, "response": body, "status": status, "elapsed_s": round(elapsed, 2)})
    return results


def response_text(body: dict) -> str:
    for key in ("message", "answer"):
        if key in body and body[key]:
            return body[key]
    return json.dumps(body, indent=2)


def write_transcript_md(results: list[dict], path: Path, meta: dict) -> None:
    lines = [
        f"# QA Transcript — {meta['tester']} ({meta['role']})",
        "",
        f"- Date: {meta['date']}",
        f"- Base URL: {meta['base_url']}",
        f"- Auth: {'bearer token' if meta['authenticated'] else 'none (unauthenticated endpoint)'}",
        "",
        "---",
        "",
    ]
    for r in results:
        lines.append(f"## Turn {r['n']} — {r['title']}")
        lines.append("")
        lines.append(f"**Sent:** {r['message']}")
        lines.append("")
        lines.append(f"**Rubric question:** {r['observe']}")
        lines.append("")
        if "error" in r:
            lines.append(f"**Result:** ERROR — {r['error']}")
        else:
            lines.append(f"**Tutor response:**")
            lines.append("")
            lines.append("> " + response_text(r["response"]).replace("\n", "\n> "))
            extras = {
                k: v for k, v in r["response"].items()
                if k not in ("message", "answer") and v not in (None, [], {})
            }
            if extras:
                lines.append("")
                lines.append(f"**Other response fields:** `{json.dumps(extras)}`")
        lines.append("")
        lines.append("**Your observation:** _[fill in]_")
        lines.append("")
        lines.append("---")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_scorecard_md(results: list[dict], path: Path, meta: dict) -> None:
    by_turn = {r["n"]: r for r in results}

    def excerpt(n: int, limit: int = 320) -> str:
        r = by_turn.get(n)
        if not r:
            return "_(turn not run)_"
        if "error" in r:
            return f"_(turn failed: {r['error']})_"
        text = response_text(r["response"]).replace("\n", " ")
        return (text[:limit] + "…") if len(text) > limit else text

    lines = [
        "# BYTELION PS#03 — QA SCORECARD",
        "",
        f"**Tester:** {meta['tester']} | **Role:** {meta['role']} | **Date:** {meta['date']}",
        f"**Frontend/Branch used:** {meta['base_url']}"
        + (f" | LLM: {meta['llm_note']}" if meta.get("llm_note") else ""),
        "",
        "> Scores below are NOT auto-computed. Read each turn's rubric question "
        "and actual response (full transcript in transcript.md / transcript.json) "
        "and fill in 0-3 per the rubric:",
        ">",
        "> 0 = Not present · 1 = Partial · 2 = Adequate · 3 = Excellent, robust across turns",
        "",
        "## METRIC SCORES",
        "",
        "| Metric | Evidence Turns | Score (0-3) | Key Observation |",
        "|---|---|---|---|",
    ]
    for code, name, turns in METRICS:
        lines.append(f"| {code}: {name} | {turns} | _/3_ | _[fill in]_ |")
    lines.append("| **TOTAL** | | **_/18_** | |")
    lines += [
        "",
        "Scoring bands: 15-18 demo-ready · 10-14 partially functional · "
        "5-9 pre-demo blockers · 0-4 fundamental pipeline issues.",
        "",
        "**TOP FINDING (1 sentence):** _[fill in]_",
        "",
        "**BLOCKER FLAG:** [Yes / No] — _[fill in: which metric scored 0 and why]_",
        "",
        "---",
        "",
        "## Evidence excerpts (auto-generated, trim as needed)",
        "",
    ]
    for turn in TURNS:
        n = turn["n"]
        lines.append(f"**Turn {n} — {turn['title']}**")
        lines.append(f"- Rubric: {turn['observe']}")
        lines.append(f"- Response excerpt: {excerpt(n)}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default="http://localhost:8000", help="Tutor backend base URL")
    parser.add_argument("--tester", default=None, help="Your name (prompted if omitted)")
    parser.add_argument("--role", default=None, help="Your role (prompted if omitted)")
    parser.add_argument("--llm-note", default=None,
                         help='Free-text note on which LLM this run used, e.g. "gpt-4o" or "claude-sonnet-5". '
                              "Scores are expected to vary by this — record it so runs are comparable.")
    parser.add_argument("--subject-id", default=None, help="subject_id to pass if the backend supports it")
    parser.add_argument("--email", default=None, help="Test account email (default: auto-generated, unique per run)")
    parser.add_argument("--password", default="TestPass123", help="Test account password")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: ./qa_run_<timestamp>)")
    args = parser.parse_args()

    tester = args.tester or input("Your name: ").strip()
    role = args.role or input("Your role: ").strip()

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./qa_run_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    email = args.email or f"qa_scorecard_{ts}@example.com"
    student_id = f"qa_scorecard_{ts}"

    print(f"BYTELION PS#03 QA scorecard runner")
    print(f"Target: {base_url}")
    print(f"Output: {out_dir}/")
    print()

    status, _ = http_json(urljoin(base_url, "/health"), None, method="GET")
    if status != 200:
        print(f"[fatal] /health check failed (status {status}) — is the server running at {args.base_url}?", file=sys.stderr)
        return 1

    print("Setting up test account...")
    try:
        token = ensure_test_account(base_url, email, args.password, "QA ScoreCard Bot", student_id)
    except ApiError as e:
        print(f"[fatal] {e}", file=sys.stderr)
        return 1
    print(f"  {'Authenticated' if token else 'No auth required on this backend'}")
    print()

    print("Running 12 scripted turns...")
    results = run_session(base_url, token, args.subject_id)
    print()

    meta = {
        "tester": tester,
        "role": role,
        "date": time.strftime("%Y-%m-%d"),
        "base_url": args.base_url,
        "authenticated": token is not None,
        "llm_note": args.llm_note,
    }

    (out_dir / "transcript.json").write_text(
        json.dumps({"meta": meta, "turns": results}, indent=2), encoding="utf-8"
    )
    write_transcript_md(results, out_dir / "transcript.md", meta)
    write_scorecard_md(results, out_dir / "scorecard.md", meta)

    failed = [r for r in results if "error" in r]
    print(f"Done. {len(results) - len(failed)}/12 turns succeeded.")
    print(f"  {out_dir}/transcript.json  — raw data")
    print(f"  {out_dir}/transcript.md    — human-readable turn-by-turn log")
    print(f"  {out_dir}/scorecard.md      — fill in the 6 metric scores from here")
    if failed:
        print(f"[warn] {len(failed)} turn(s) failed — see transcript for details", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
