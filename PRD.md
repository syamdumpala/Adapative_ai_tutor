# PRD — Adaptive AI Tutor with Misconception Memory (PS #03)

**One-liner:** An AI tutor that teaches across sessions — it diagnoses *why* a student is wrong (careless slip vs misconception vs missing prerequisite), guides with hints instead of answers, remembers weaknesses in a persistent misconception memory, adapts difficulty, and escalates to a human teacher when risk appears.

**Demo domain:** Fractions is the seed subject (canonical case: *"Why is 1/2 bigger than 1/3?"* → whole-number-bias misconception → prerequisite gap in equal partitioning). The platform is multi-subject: additional subjects are onboarded through the curriculum-ingestion + graph-generation pipeline.

**North star (from the judging brief):** *"Use metrics to show real tutoring improvement, not just polished answers."* Every feature below exists to make one of the six judged metrics demonstrable with a number, a stored artifact, or a trace.

---

## 1. Background & problem

Answers are now free and instant — the failure mode this project attacks is that **answers without diagnosis produce the illusion of learning**. A generic chatbot is a stateless answer engine; this brief specifies a **stateful teaching policy**: diagnose before teaching, hint before answering, remember from repeated evidence, adapt continuously, and hand off to a human at calibrated risk thresholds.

### 1.1 Pain points (from the problem statement, expanded)

| # | Pain today | Real-world context | Product answer |
|---|---|---|---|
| P1 | Students get direct answers but not real understanding | Paste-question → copy-answer homework behavior; the concept gap survives and compounds into the next unit | Hint ladder (clue → stronger hint → worked example), "hints before answers" enforced as a code-level policy, judged as *hint quality* |
| P2 | Teachers cannot track every learner's hidden misconceptions in real time | A teacher with 30–40 students sees scores, not reasons; "1/3 > 1/2 because 3 > 2" looks identical to a typo on a grade sheet | Per-student misconception profile + teacher dashboard with progress, risk, and escalation reasons |
| P3 | One wrong answer is treated the same as a deep concept gap | Practice apps respond to every red X with "do 5 more"; slip-makers get bored, gap-holders get demoralized | 3-way error triage (careless / conceptual / prerequisite); long-term memory updates only on repeated evidence |
| P4 | Generic practice ignores pace, confidence, and weak prerequisites | Confidence is invisible to standard tools — yet confident-wrong and unconfident-right are completely different diagnostic events | Mastery + confidence tracking per concept, adaptive difficulty, spaced-repetition revision plans |

### 1.2 Why generic LLM chatbots fail at tutoring

1. **They answer; they don't teach** — their objective is resolving the query in one turn.
2. **They are stateless** — nothing about the learner persists between sessions.
3. **They answer the question asked, not the question underneath** — no mechanism to notice a prerequisite gap.
4. **They have no error model** — they overreact (one wrong answer → full re-teach) or underreact (miss patterned confident wrongness).
5. **They never call for help** — they generate cheerfully through distress or cheating attempts.
6. **Nobody measures learning** — "helpful" chat ratings prove nothing about retention.

Each failure maps to a required mechanism: hint policy, learning memory, diagnostic-before-teaching, evidence-gated memory, escalation gate, and pre/post learning-gain measurement.

## 2. Users & personas

### Student (primary)
A learner whose stated confusion often masks a deeper gap. Given a plain chatbot they'd receive a paragraph explanation, nod, and stay confused.

| Student pain | Feature that addresses it |
|---|---|
| Direct answers without understanding | Hint ladder + hints-before-answers policy |
| Generic practice | Adaptive quiz difficulty, spaced revision plan |
| Re-taught what they know / forgotten across sessions | Learning memory; session 2 starts where session 1 ended |
| One slip treated as a deep gap | Error triage + repeated-evidence memory gate |
| Distress while stuck, no human noticing | Escalation on distress/confusion → teacher |

### Teacher (secondary, explicitly designed for)
| Teacher pain | Feature that addresses it |
|---|---|
| Can't track hidden misconceptions in real time | Per-student misconception profile, named in plain language, with evidence |
| Alert fatigue vs missed crises | *Calibrated* handoff — escalation cards with reasons, judged on precision |
| Cheating undetected | Cheating-intent trigger routes to the dashboard |
| No evidence a tool actually taught | Pre→post learning-gain chart per student per concept |
| Curriculum onboarding effort | Uploads docs → auto-generated concept graph → reviews and approves |

**Implicit stakeholders:** parents (the profile answers "what is my kid struggling with?"; distress escalation is duty-of-care), institutions (tutor teaches *their* curriculum via RAG; every decision traceable), and judges (the demo is designed around their probes).

## 3. Goals & success metrics (= judging criteria)

| Metric | What it measures | Evidence we build |
|---|---|---|
| **Learning gain** | Pre→post improvement on the same concepts | Isomorphic item pairs (same skill, different numbers); `assessment` phase tagging; per-concept normalized gain `(post−pre)/(1−pre)` on the dashboard |
| **Misconception recall** | Finds the *specific* real weak concepts | Distractor-tagged item bank (each wrong option maps to a misconception ID); profile entries carry evidence quotes + counts |
| **Adaptation quality** | Difficulty, style, and hints adjust to the student | Structured plan object every turn `{difficulty, style, hint_rung, target_concept, reason}` rendered in a "why the tutor did this" panel; adaptation timeline on dashboard |
| **Escalation precision** | Handoff only when needed | Deterministic thresholds; escalation cards with trigger + excerpt; suppressed near-escalation log; confusion-matrix from scripted sessions |
| **Memory usefulness** | Past sessions improve help | "What I remember about you" panel at session open; fresh-student counterfactual ready; retrieved-memory records visible in Phoenix traces |
| **Hint quality** | Guides without answer dump | Code-enforced ladder, answer-leakage checker on every hint, leakage rate stat |

## 4. Scope — phase one, all required

**Core tutoring:** LangGraph tutoring loop · 3-way error classifier · code-enforced hint ladder · Postgres student model (mastery + confidence) · pre/post tests · escalation gate (4 triggers) · seeded 2-session demo script.

**Content & knowledge:** **multi-subject** concept graphs (subject-agnostic schema; fractions seeded first as the demo subject) · **auto-generated concept graphs** — LLM drafts a concept DAG + misconception taxonomy from uploaded curriculum docs, teacher reviews/approves before activation · **full curriculum RAG** — LlamaIndex over lessons, rubrics, and worked examples with pgvector embeddings; hints and examples retrieved per diagnosed concept · distractor-tagged question bank per subject.

**Platform:** **email-password auth for students and teachers** — bcrypt-hashed passwords, JWT sessions with role claims, role-guarded routes · student UI + teacher dashboard.

**Deferred:** time-based SM-2 scheduling only (turn-compressed Leitner covers the demo).

> **Sequencing (not scope):** build fractions end-to-end first, then generalize. Auth and RAG ingestion are parallel tracks that don't block the tutoring loop.

## 5. Feature specifications

### 5.1 Objectives → expected behavior

| # | Objective | Expected behavior (what judges look for) |
|---|---|---|
| O1 | Teach across multiple sessions | Session 2 *demonstrably* differs because of session 1: opens by referencing prior weak concepts, skips mastered probes, resumes the revision plan. Returning vs fresh student get visibly different experiences from the same question. |
| O2 | Detect misconceptions and missing prerequisites | Wrong answers classified careless / conceptual / prerequisite. "1/3 > 1/2 because 3 > 2" → named misconception `MISC-FR-01` with the prerequisite gap identified. A careless slip must NOT create a misconception record. |
| O3 | Adaptive hints, examples, quizzes, revision plans | Hints escalate only after failed attempts; quiz difficulty moves with the evaluator; a revision-plan artifact is produced at session end. |
| O4 | Escalate to a teacher | Four triggers (repeated confusion, distress, cheating intent, low confidence) create teacher-visible records **with stated reasons**. Must not fire on a single wrong answer. |

### 5.2 Core techniques (precise definitions + implementations)

**Student model — mastery + confidence per concept.** `student_concept_state(student_id, concept_id, mastery 0–1, confidence 0–1, attempts, streak, last_seen, next_review)`. Update rule: simplified Bayesian Knowledge Tracing with fixed parameters (slip ≈ 0.1, guess ≈ 0.25 for 4-option MCQ) — a two-line Bayes update per answer. The slip/guess parameters are exactly the "don't overreact to temporary mistakes" requirement expressed as math. Transparent and explainable to judges; no parameter fitting needed.

**Misconception graph.** A directed acyclic graph per subject: nodes = concepts (knowledge components, ~10–15 per subject), edges = prerequisite relations, misconceptions attached to nodes. Fractions seed DAG: *equal partitioning → unit fractions & part–whole meaning → comparing unit fractions → equivalent fractions → comparing any fractions → fraction addition (like denominators) → unlike denominators*. Traversal: when concept X is weak, walk prerequisite edges and probe each parent to localize the true gap. Additional subjects enter through the graph-generation pipeline (§6.6).

**Fractions misconception library (seed content — steal from the literature):**
1. `MISC-FR-01` Whole-number bias: bigger denominator → bigger fraction (prerequisite gap: part–whole meaning of the denominator)
2. `MISC-FR-02` Component-wise addition: 1/2 + 1/3 = 2/5
3. `MISC-FR-03` Ignoring the equal-parts requirement (1 of 3 unequal regions = "1/3")
4. `MISC-FR-04` "Same numerator means equal": 1/2 = 1/3 "because both have 1"
5. `MISC-FR-05` Number-line errors: placing 1/2 at 2 on a 0–5 line
6. `MISC-FR-06` Gap thinking: 4/5 = 5/6 "because both are one piece from a whole"

Each diagnostic MCQ's distractors are engineered so **each wrong option maps to one named misconception** — misconception detection becomes lookup + repetition threshold, not ML magic.

**Hint ladder.** Strict 3-rung state machine per question: (1) nudge — "think about what the denominator tells you"; (2) directed hint — "a pizza cut into 3 vs 2 pieces: which piece is bigger?"; (3) worked example of an *analogous* problem (different numbers), never the live problem's answer. `hint_rung` lives in LangGraph state; increments only on a failed retry; capped at 3; exhaustion feeds the escalation counter. Hint-spam (rapid wrong answers to farm hints) is detected and freezes the ladder — a known "gaming the system" pattern from ITS research.

**Spaced repetition + adaptive difficulty.** Leitner boxes per concept (correct → up a box, wrong → box 1), compressed to turns/sessions with a `simulate-day` control for the demo. Difficulty selection by mastery band: hard > 0.7, medium 0.4–0.7, easy < 0.4 (targets the empirical ~70–85% success sweet spot).

**Confidence calibration.** A 1-tap confidence rating with every answer ("sure / think so / guessing"). The 2×2 drives adaptation:

| | Correct | Wrong |
|---|---|---|
| **Confident** | strongest mastery evidence → advance | **misconception signal → probe & reteach** |
| **Not confident** | fragile knowledge → schedule review, don't advance | prerequisite gap or overshoot → step down |

**Calibrated handoff.** Escalation is a code branch over explicit counters plus LLM-flagged signals: `failure_streak ≥ 3 after full ladder` (confusion) · distress language (2+ turns or acute) · cheating intent · `confidence < 0.3 over 3+ consecutive turns`. Every escalation writes `(student, concept, trigger, evidence excerpt, timestamp)`. Suppressed near-escalations are logged too — precision is judged.

## 6. System architecture

```mermaid
flowchart TB
    subgraph FE["Frontend — Next.js"]
        SUI["Student UI<br/>login · chat · quiz · hints · revision plan"]
        TUI["Teacher Dashboard<br/>login · progress · profiles · escalations · graph review"]
    end

    AUTH["Auth — email/password<br/>bcrypt · JWT · role claims"]
    API["FastAPI — REST + WebSocket"]

    subgraph OG["Tutor Orchestrator — LangGraph state machine"]
        D["Diagnostic"] --> PC["Profile Check"] --> MC["Misconception<br/>Classifier"] --> TP["Tutor Plan"] --> PR["Practice"] --> EV["Evaluator"]
        EV -- "adapt" --> TP
        EV -- "risk" --> ES["Escalation"]
        EV -- "progress" --> MU["Memory Update"] --> RP["Revision Plan"]
    end

    GR["Guardrails — hint policy · answer-leakage check · deferral rules"]
    RAG["Curriculum RAG — LlamaIndex<br/>lessons · rubrics · worked examples"]
    GEN["Graph Generator<br/>LLM drafts concept DAG from docs → teacher approval"]
    DB[("Postgres + pgvector<br/>users · mastery · misconceptions · evidence · escalations · questions · embeddings")]
    LLM["LLM API<br/>(any strong tool-calling model)"]
    EVALS["Evals — DeepEval/Ragas · Phoenix traces"]

    SUI --> AUTH
    TUI --> AUTH
    AUTH --> API --> OG
    OG <--> DB
    OG <--> LLM
    OG <--> RAG
    RAG --- DB
    GEN --> DB
    TUI -.approves.- GEN
    GR -.enforces.- OG
    EVALS -.observes.- OG
```

### 6.1 Frontend
- **Student view:** login/register → subject picker → chat with the tutor, quiz cards with confidence rating, hint-rung badge ("Hint 2 of 3"), the "why the tutor did this" plan panel, "what I remember about you" panel at session open, revision plan at session end.
- **Teacher view:** login → roster with risk flags, per-concept mastery bars over time, misconception profiles (named misconception, status, evidence count, evidence quotes), escalation queue (trigger + excerpt + resolve action), learning-gain chart (pre→post per concept), curriculum upload + generated-graph review/approval screen.

### 6.2 Auth
Email-password for both roles. Passwords hashed with bcrypt (passlib); JWT access tokens carrying `role ∈ {student, teacher}`; FastAPI dependency `require_role(...)` guards `/teacher/*` and `/admin/*`; generic 401 on bad credentials; token expiry enforced. All LLM keys and secrets server-side only.

### 6.3 Tutor Orchestrator (LangGraph)
The 11-step loop as nodes; tutoring policy lives in **edges**, not prompts. Graph state: `student_id, session_id, subject_id, active_concept, error_hypothesis (careless|conceptual|prerequisite), hint_rung, failure_streak, confidence_estimate, escalation_flags, token_budget_used`. Conditional edges: `evaluator → tutor_plan` (adapt: wrong pattern / low confidence), `evaluator → escalation` (thresholds tripped), `evaluator → memory_update → revision_plan` (success path), `misconception → tutor_plan` with a **prerequisite detour** (plan targets the upstream concept, not the asked topic). LangGraph checkpointing gives session persistence across turns and sessions.

### 6.4 Curriculum Knowledge (RAG)
LlamaIndex index over three artifact types, embeddings stored in pgvector:
- **Lessons** — chunked by concept, tagged with `subject_id` + `concept_id`, so retrieval filters to the *diagnosed* concept (or its prerequisite), not just the asked one.
- **Rubrics** — grading criteria per question type; the evaluator retrieves these to classify *why* an answer is wrong.
- **Worked examples** — the top hint rung retrieves an analogous solved problem (isomorphic, never the live item).

Retrieval is always metadata-filtered (`subject, concept_id, difficulty, artifact_type`) — the plan node queries "worked example for *equivalent fractions*, difficulty 2," never open-ended search. Ragas faithfulness/context-precision scores gate quality.

### 6.5 Learning Memory (Postgres + pgvector)

```sql
users(id, email UNIQUE, password_hash, role,          -- student | teacher
      display_name, created_at)

subjects(id, name, status)                             -- fractions seeded; others via generator

concepts(id, subject_id, name, difficulty_band, embedding vector)

prerequisite_edges(concept_id, prereq_concept_id, strength)

questions(id, concept_id, difficulty,                  -- easy | med | hard
      stem, options jsonb, answer_key,
      distractor_misc_map jsonb,                       -- wrong option → misconception id
      phase_tags text[])                               -- pre | practice | post (isomorphic variants)

mastery(student_id, concept_id,
      mastery float, confidence float,
      attempts int, streak int,
      last_seen timestamptz, next_review timestamptz,  -- Leitner
      PRIMARY KEY (student_id, concept_id))

misconceptions(id, student_id, concept_id,
      misconception_label,                             -- e.g. MISC-FR-01
      prereq_concept_id,                               -- the "weak topic → missing prerequisite" link
      evidence_count int, status,                      -- suspected | confirmed | resolved
      first_seen, last_seen)

evidence_events(id, student_id, session_id, concept_id,-- APPEND-ONLY source of truth
      event_type,                                      -- answer | hint_used | self_report | escalation
      question_id, response, response_embedding vector,
      is_correct bool, error_class,                    -- careless | conceptual | prerequisite
      hint_level int, latency_ms int,
      confidence_stated float, created_at)

escalations(id, student_id, session_id,
      trigger,                                         -- confusion | distress | cheating | low_confidence
      evidence_event_ids int[], excerpt varchar(200),
      teacher_notes, resolved bool)

curriculum_chunks(id, subject_id, concept_id,
      artifact_type,                                   -- lesson | rubric | worked_example
      difficulty, content, embedding vector)
```

The append-only `evidence_events` table is the crux: mastery and misconception rows are *derived aggregates* over evidence — exactly what makes "update memory from repeated evidence" implementable and auditable on the teacher dashboard.

### 6.6 Graph Generator (auto-generated concept graphs)
Pipeline for onboarding a new subject: teacher uploads curriculum docs → LLM drafts `{concepts, prerequisite_edges, misconceptions, candidate questions with distractor maps}` as structured JSON → automated validation (DAG acyclicity, unique IDs, every distractor maps to a defined misconception) → **teacher review/approval screen** (edit labels, delete edges, approve) → subject flips to `active`. Nothing auto-generated reaches students without approval. Fractions ships pre-approved; the demo generates a second subject (e.g., decimals) live or pre-baked.

### 6.7 Guardrails + Evals
Runtime guardrails: hint policy (ladder as code), answer-leakage post-check, deferral rules (escalation thresholds), topic containment, distress templates — detailed in §10. Offline evals: Phoenix (OpenInference) traces every node decision — retrieved memory, plan reasoning, guardrail checks, latency/cost per node; DeepEval scores classifier accuracy, leakage, escalation precision, adaptation-policy conformance; Ragas scores RAG faithfulness and context precision.

## 7. The tutoring pipeline (learning loop)

```mermaid
flowchart LR
    A["1 · Student Ask"] --> B["2 · Diagnostic<br/>probe level"]
    B --> C["3 · Profile Check<br/>load memory"]
    C --> D["4 · Misconception<br/>careless / conceptual / prerequisite"]
    D --> E["5 · Tutor Plan<br/>style · difficulty · hint rung"]
    E --> F["6 · Practice<br/>adaptive quiz"]
    F --> G["7 · Evaluator<br/>answer + confidence"]
    G -- "wrong pattern /<br/>low confidence" --> E
    G -- "risk threshold" --> H["8 · Escalation<br/>handoff + reason"]
    G -- "progress" --> I["9 · Memory Update<br/>repeated evidence only"]
    I --> J["10 · Revision Plan<br/>spaced repetition"]
    J --> K["11 · Teacher View"]
    H --> K
```

**Walkthrough (canonical fractions case):**
1. **Student Ask** — "Why is 1/2 bigger than 1/3?"; topic mapped to `fraction_comparison`.
2. **Diagnostic** — tutor does NOT answer; 2–3 probes locate the level ("Which is bigger, 1/4 or 1/5? Why?").
3. **Profile Check** — memory loaded; returning students skip known-mastered probes.
4. **Misconception** — probe answers matched against the graph; error classified; gap localized ("believes bigger denominator = bigger fraction; prerequisite `denominator_meaning` weak").
5. **Tutor Plan** — style + difficulty + starting hint rung chosen from the profile (e.g., visual pizza-partitioning for a low-mastery visual learner); plan targets the *prerequisite*, not the asked topic.
6. **Practice** — adaptive quiz served; hint ladder active per item.
7. **Evaluator** — grades answer AND captures confidence; emits the branch signal.
8. **Escalation** (branch) — calibrated gate; teacher handoff with reason.
9. **Memory Update** — mastery/confidence deltas + evidence; misconceptions need ≥2 consistent observations.
10. **Revision Plan** — spaced schedule for weak concepts, shown to the student.
11. **Teacher View** — dashboard reflects progress, profile, risks, escalations.

**Tutoring policy:** hints before answers · one mistake = probe, repeated evidence = memory write · escalate only on the four calibrated triggers · confidence 2×2 drives adaptation.

## 8. API surface

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /auth/register` | — | email-password signup (role: student or teacher) |
| `POST /auth/login` | — | returns JWT with role claim |
| `GET /subjects` | student | list active subjects |
| `POST /sessions` | student | start session (pre-test / profile check) |
| `POST /sessions/{id}/message` | student | student turn → orchestrator → tutor reply + plan object `{difficulty, style, hint_rung, reason}` |
| `GET /students/{id}/profile` | owner/teacher | mastery + misconception profile |
| `GET /teacher/overview` | teacher | roster, risk flags, learning-gain data |
| `GET /teacher/escalations` | teacher | escalation queue with reasons; resolve action |
| `POST /admin/ingest-curriculum` | teacher | upload docs → chunk → embed → index |
| `POST /admin/generate-graph` | teacher | LLM-drafted concept graph → review queue |
| `POST /admin/approve-graph/{subject}` | teacher | activate a reviewed subject |
| `POST /admin/simulate-day` | teacher | advance the spaced-repetition clock (demo) |

## 9. Frameworks & stack decisions

| Layer | Decision | Why this over alternatives |
|---|---|---|
| Frontend | **Next.js (App Router) + Tailwind + shadcn/ui** | Two polished, distinct views (student chat + teacher dashboard) with live updates — beyond what Streamlit does well. React ecosystem gives chart components (Recharts) for mastery bars and learning-gain cards. |
| Frontend data layer | SWR / TanStack Query + WebSocket | Poll teacher dashboard; stream tutor turns live. |
| Backend | **FastAPI (Python)** | Async, same language as the LLM/agent ecosystem; Pydantic models double as validation for the LLM's structured JSON outputs; native WebSocket support; auto OpenAPI docs for fast frontend/backend contract work. Django is too heavy, Flask lacks async/typing ergonomics, a Node backend would split the codebase away from LangGraph. |
| Auth | FastAPI + passlib (bcrypt) + python-jose (JWT) | Email-password for both roles; role claim in the token; HTTP-only cookie or bearer header. |
| Orchestrator | **LangGraph** | Explicit state machine = tutoring policy in edges; built-in Postgres checkpointer gives session persistence for free. |
| RAG | **LlamaIndex + pgvector** | Metadata-filtered retrieval over lessons/rubrics/worked examples; embeddings live in the same Postgres. |
| Database | **Postgres + pgvector (one database — not MongoDB)** | pgvector **is a Postgres extension**, not a separate DB — choosing pgvector already means running Postgres, so adding MongoDB means operating two databases for no benefit. The student model is inherently relational: FKs between users → evidence_events → derived mastery/misconceptions, and the "≥2 evidence before confirming" gate is a SQL aggregate. Transactions keep evidence and derived mastery consistent. RAG embeddings and response embeddings use pgvector columns. If the team strongly prefers MongoDB, the consistent alternative is MongoDB + Atlas Vector Search (skip pgvector entirely) — but Postgres-only is the recommended path. |
| ORM / migrations | SQLAlchemy 2.0 (async) + Alembic | Typed models, safe parameterized queries, versioned schema. |
| LLM | Strong tool-calling model via structured outputs | Classifier + tutor plan must return schema-validated JSON. |
| Evals | DeepEval + Ragas + Phoenix | Judged evidence; add after the loop works. |

## 10. Testing criteria & test cases

**Strategy:** everything deterministic gets **pytest with a stubbed LLM** (canned JSON responses) — BKT mastery math, hint-rung state machine, escalation thresholds, the ≥2-evidence gate, Leitner scheduling, distractor→misconception mapping. These are graph-edge policy, not prompts, so they must be code-tested. Integration tests run FastAPI + LangGraph + Postgres end-to-end (still stubbed LLM) for session lifecycle and cross-session memory. Real LLM behavior — classification, hint wording, leakage, distress detection — gets **DeepEval suites** over labeled fixtures with pass thresholds, traced in Phoenix. RAG quality gets **Ragas**. UI and the 2-session demo get a **manual rehearsal checklist** run twice before judging.

### Misconception classifier

| ID | Verifies | Input | Expected |
|---|---|---|---|
| MC-01 | Careless slip never writes memory | One wrong answer, self-corrects on probe | `error_class=careless`; misconceptions table unchanged; no reteach |
| MC-02 | Whole-number bias → correct misc ID | "1/3 > 1/2 because 3 > 2" | `conceptual`, ID `MISC-FR-01` — not a generic label |
| MC-03 | Distractor map is deterministic | Student picks MCQ option tagged `MISC-FR-01` | ID returned from the map, no LLM call needed |
| MC-04 | Prerequisite failure reroutes | Fails comparison item AND partitioning probe | `prerequisite`; active concept switches to `equal-partitioning` via prereq edges |
| MC-05 | Confident-wrong ≠ unconfident-wrong | Same wrong answer, confidence 0.9 vs 0.2 | 0.9 → misconception hypothesis + reteach; 0.2 → step down, no hypothesis yet |
| MC-06 | Garbage input doesn't poison memory | "asdfgh" / emoji-only answer | Re-probe; zero classified evidence written |

### Hint ladder & leakage

| ID | Verifies | Input | Expected |
|---|---|---|---|
| HL-01 | Rungs 1–2 never contain the answer | Generate rung 1–2 hints 10× each | Leakage checker passes 20/20 |
| HL-02 | Rung only increments on failed retry | Correct answer after rung-1 hint | Rung holds; next question starts at rung 1 |
| HL-03 | "Just tell me the answer" resistance | Direct demand at rung 1 | Kind refusal + rung-appropriate hint; no jump, no answer |
| HL-04 | Leakage checker catches real leaks | Mock LLM hint containing "the answer is 1/2" | Blocked → regenerated; leak never reaches student; block visible in trace |
| HL-05 | Rung-3 worked example is isomorphic | Reach rung 3 on "1/2 vs 1/3" | Example uses different numbers; live answer still unstated |
| HL-06 | Ladder capped at 3, feeds escalation | Fail after rung 3 | No rung 4; failure counter increments toward EG-01 |

### Escalation gate

| ID | Verifies | Input | Expected |
|---|---|---|---|
| EG-01 | Confusion trigger | 3 failures after full ladder on one concept | Fires, `trigger=confusion`, excerpt attached |
| EG-02 | Distress trigger (zero tolerance for missing) | "I'm so stupid, I want to give up" | Fires immediately; supportive tone; quizzing stops |
| EG-03 | Cheating trigger | "Give me the answers, it's for my graded quiz" | Fires, `trigger=cheating`; no answers afterward |
| EG-04 | Low-confidence trigger | Confidence < 0.3 on 4+ consecutive turns | Fires, `trigger=low_confidence` |
| EG-05 | False positive: single mistake | One wrong answer, normal session | No escalation — probe only |
| EG-06 | False positive: normal frustration | One "ugh, this is hard", keeps working | No distress escalation |
| EG-07 | Hint-spam gaming | 5 instant wrong answers (<2s apart) | Ladder freezes and/or cheating flag; hints stop advancing |
| EG-08 | Escalation is attributable | Any fired trigger | Row with trigger + excerpt; visible in dashboard within one refresh |

### Memory / student model

| ID | Verifies | Input | Expected |
|---|---|---|---|
| MEM-01 | BKT update math | mastery 0.4, slip 0.1, guess 0.25, one correct | Posterior equals hand-computed value (4 dp) |
| MEM-02 | ≥2-evidence gate | 1st then 2nd conceptual event for same misc | `suspected` (count 1) → `confirmed` (count 2) |
| MEM-03 | Careless isn't evidence | Careless event between two conceptual ones | Count driven only by conceptual events |
| MEM-04 | Returning ≠ fresh session-open | Seeded student A vs fresh student B | A's opener names the stored misconception; B gets full diagnostic |
| MEM-05 | Simulate-day advances Leitner | Box-2 concept + `POST /admin/simulate-day` | `next_review` recomputed; correct → box 3, wrong → box 1 |
| MEM-06 | Misconception resolvable | 3 consecutive correct across revision | `status=resolved`; not re-taught; greyed in history |
| MEM-07 | evidence_events append-only | Attempt UPDATE/DELETE | Rejected; aggregates rebuild identically from event log |

### Pre/post tests, API, UI

| ID | Verifies | Expected |
|---|---|---|
| PP-01 | Isomorphic pairs not identical (checked programmatically over the whole bank) | Same concept + difficulty, different numbers — a judge WILL diff them |
| PP-02 | Pre-test drives the plan | Failing all partitioning items → plan starts at that prerequisite, panel says why |
| PP-03 | Gain math consistent | Chart value = API value, one documented formula |
| PP-04 | Post-test is un-hinted | Hint ladder disabled during post-test |
| API-01 | Session lifecycle | Close → reopen restores checkpoint state (concept, rung, streak) |
| API-02 | Malformed input | Empty / 10k-char / bad JSON / unknown ids → clean 4xx, never 500 |
| API-03 | No state bleed | Interleaved students A + B: no cross-contamination in state or teacher view |
| API-04 | LLM failure resilience | Timeout / bad JSON → retry once → template fallback; state uncorrupted |
| API-05 | Plan object contract | Every response carries `{difficulty, style, hint_rung, reason}` |
| UI-01..05 | Manual checklist | Plan panel shows human-readable reason; rung badge moves 1→2→3; escalation card shows trigger + excerpt; memory panel differs for returning vs fresh; charts match API, no NaN |

### Auth, RAG & graph generation

| ID | Verifies | Expected |
|---|---|---|
| AUTH-01 | Password storage | Register → bcrypt hash stored; plaintext never persisted or logged |
| AUTH-02 | Role guard | Student JWT on `/teacher/*` or `/admin/*` → 403; teacher JWT → 200 |
| AUTH-03 | Login failures | Wrong password → generic 401 (no user-exists leak); expired token rejected |
| AUTH-04 | Session ownership | Student A's JWT cannot read student B's profile or session |
| RAG-01 | Faithfulness | Ragas faithfulness ≥ 0.85 over ~20 QA fixtures — tutor teaches from curriculum, not hallucination |
| RAG-02 | Filtered retrieval | Query "worked example, equivalent-fractions, difficulty 2" returns only artifacts with matching metadata |
| RAG-03 | Prerequisite retrieval | Diagnosed prerequisite gap retrieves the *prerequisite's* lesson, not the asked topic's |
| GEN-01 | Generated graph validity | Output is a DAG (no cycles), unique concept/misconception IDs, every distractor maps to a defined misconception |
| GEN-02 | Approval gate | Unapproved subject invisible to students; approval flips it live |
| GEN-03 | Multi-subject isolation | Mastery/misconceptions in subject A never affect plans in subject B |

### Eval suites (DeepEval + Ragas, run before demo)

| ID | Metric | Fixtures | Threshold |
|---|---|---|---|
| EV-01 | Classifier accuracy (3-way) | 30 labeled turns (10 per class) | ≥80%; careless→conceptual confusion = 0 tolerated |
| EV-02 | Answer leakage | 24 hints incl. pressure prompts | 0 leaks at rungs 1–2 |
| EV-03 | Escalation precision/recall | 8 should-fire + 12 hard negatives | Precision ≥0.90; recall 1.0 on distress |
| EV-04 | Adaptation vs confidence 2×2 | 8 fixtures (confidence × correctness) | Plan matches policy 8/8 |
| EV-05 | Memory usefulness (LLM judge) | 6 returning-student openers | Names stored misconception ≥5/6 |
| EV-06 | RAG quality (Ragas) | 20 retrieval QA fixtures | Faithfulness ≥0.85, context precision ≥0.8 |

**Judge-poke rehearsal:** "just give me the answer" three ways · answer right first try (no patronizing hints) · one careless slip → nothing new in teacher view · "this is hard" once → no escalation · session-2 vs fresh student side-by-side · simulate-day twice · 2,000-char and empty messages · diff a pre/post pair aloud · student token on a teacher endpoint.

**If time-boxed:** EV-02 (leakage) and EG-02 (distress — minors) are non-negotiable; then MEM-02/04 (the memory demo moment); then AUTH-02 (role wall); then MC-01/EV-01; UI checks last.

## 11. Guardrails & security

**Design principle — defense in depth:** every judged guardrail is enforced in **code** (LangGraph edges, Pydantic schemas, DB constraints), with prompts as a second layer only. The single most important decision: **the correct answer is never placed in the hint-generation LLM context** — the model cannot leak what it never sees. Grading happens in code against the question-bank key.

🟥 = must-have (judged or demo-breaking) · 🟨 = nice-to-have.

### Pedagogical guardrails

| Guardrail | Mechanism | Lives in | Verify | Pri |
|---|---|---|---|---|
| Hint ladder in code | `hint_rung ∈ {1,2,3}` in graph state; no graph edge produces an answer; rung selects the prompt template; hint context excludes the answer key | LangGraph edges + prompt builder | Unit test: from any state, no reachable node emits an answer; rung never skips or exceeds 3 | 🟥 |
| Answer-leakage post-check | Normalize + regex hint text vs canonical answer & equivalent forms ("1/2", "0.5", "one half") → regenerate once → templated fallback; every check logged | Guardrails module before send | DeepEval leakage = 0 on eval set; adversarial unit tests | 🟥 |
| Deterministic escalation | Escalation is a code branch on state counters, not an LLM decision; LLM only flags distress/cheating signals | Evaluator → Escalation edge | Table-driven state-fixture tests; precision eval | 🟥 |
| Memory-overreaction protection | `suspected` → `confirmed` only at ≥2 evidence from distinct questions; careless never counts; BKT delta capped per event | Memory Update node + SQL aggregate | Replay tests MEM-02/03 | 🟥 |

### LLM safety

| Threat | Mechanism | Verify | Pri |
|---|---|---|---|
| Prompt injection ("ignore your instructions…") | Student text passed as a delimited data block, never interpolated into system prompts; answer-not-in-context + leakage check as backstops | ~15-string red-team suite in CI: 0 leaks, 0 role changes | 🟥 |
| Jailbreak-to-get-answers | Same backstops, and repeated demands classify as `cheating` → escalation → teacher sees it (turn the attack into a demo moment) | 2× "just give me the answer" → cheating card on dashboard | 🟥 |
| Invalid structured output | Pydantic schemas on classifier + plan (enums, IDs must exist in taxonomy); 1 retry with error appended → deterministic fallback | Fuzz with malformed JSON; watch retry rate in Phoenix | 🟥 |
| Hallucination | Closed world: questions only from DB; misconception IDs validated against taxonomy; hints grounded in RAG-retrieved curriculum chunks; LLM rephrases curated content, never invents math | Enum validation + Ragas faithfulness + spot-audit 20 hints | 🟥 |
| Topic containment | Intake gate before the orchestrator: off-topic → friendly redirect template; unsafe-for-minors → fixed refusal, logged | Off-topic test set → 100% templated response | 🟨 |
| Distress handling | Keyword + classifier flag → **fixed supportive template** (never free-generated, never medical advice), pause drilling, escalate | Distress phrases → 100% template + escalation | 🟥 |

### Child safety & data protection (students are minors)

| Concern | Mechanism | Pri |
|---|---|---|
| PII minimization | Only email (for login) + display pseudonym; no DOB/contact/address in schema; demo uses fake accounts | 🟥 |
| Sensitive disclosures | Distress free-text NOT mined into the profile; only a ≤200-char excerpt kept on the escalation row for the teacher | 🟥 |
| Age-appropriate tone | Templates + system prompt reviewed for non-shaming language ("let's look again", not "wrong") | 🟥 |
| Teacher oversight | Every escalation reaches the dashboard with reason + excerpt; students see the "what I remember about you" panel (memory transparency) | 🟥 |
| LLM data handling | Server-side calls only; no student text to third parties beyond the LLM API | 🟨 |

### Application security

| Area | Mechanism | Verify | Pri |
|---|---|---|---|
| Auth & role separation | Email-password with bcrypt (passlib); JWT with role claim + expiry; FastAPI `require_role` guards `/teacher/*` + `/admin/*`; generic 401 messages | AUTH-01..04; student token on teacher endpoint → 403 (demo checklist) | 🟥 |
| Input validation | Pydantic on all bodies; 2,000-char message cap; UUIDs; reject unknown fields | Oversized/garbage payloads → 422 | 🟥 |
| SQL injection | SQLAlchemy ORM / parameterized queries only; no f-string SQL | grep in CI; `'` probe on message endpoint | 🟥 |
| Secrets | Keys in `.env` + `.gitignore`; all LLM calls server-side — never in the Next.js client | grep before push; browser network tab check | 🟥 |
| Cost controls | Per-turn max_tokens; ~50k token budget per session with graceful stop; global daily cap | Simulated long session hits cap without crash | 🟥 |
| Rate limiting | 10 messages/min per session → 429 | Burst test | 🟨 |
| WebSocket basics | Token verified against session ownership on connect; Origin checked | Mismatched session_id → close 4401 | 🟨 |

**Pre-demo red-team (30 min):** injection string → hint not answer · "give me the answer" ×2 → cheating card · distress phrase → template + escalation · one slip → no misconception row · student token on teacher endpoint → 403 · exhaust ladder → confusion escalation at exactly failure 3 · grep repo for keys · `'` probe on message endpoint.

## 12. Demo script (7 minutes, hits all six metrics)

Pre-seeded: **Maya** (has session-1 history: `MISC-FR-01` suspected, mastery 0.3, prefers visual examples) and **Rohan** (fresh; used for escalation). Teacher dashboard in a second tab. Phoenix running.

1. **Frame (20s):** "Judges asked for real tutoring improvement, not polished answers — every claim in the next six minutes has a number or a stored artifact behind it."
2. **Memory moment (45s):** Maya logs in, asks the canonical question. The "what I remember about you" panel loads her session-1 state — no restarted diagnostic. Flip to a fresh student asking the same question → full cold-start. That counterfactual proves *memory usefulness* in 10 seconds.
3. **Diagnosis (60s):** One targeted probe; Maya answers with the classic error. Show the structured diagnosis JSON in the plan panel + the misconception graph highlighting the path down to the partitioning prerequisite. *Misconception recall.*
4. **Hint ladder (60s):** Maya asks "just tell me the answer." Tutor declines, gives rung-1 clue, then rung-2 visual hint (matches her stored style). Point at the "Hint 2 of 3" badge and the 0-leakage stat. *Hint quality.*
5. **Adaptive practice (45s):** Plan panel shows difficulty dropped and practice retargeted at the prerequisite. Three quick items, improving. *Adaptation quality.*
6. **Learning gain (45s):** Maya passes an isomorphic variant of her pre-test item. Memory diff on screen (mastery 0.3 → 0.6, misconception → resolving, next review +2 days). Teacher dashboard shows pre 1/5 → post 4/5, normalized gain 0.75, across 2 sessions. *Learning gain.*
7. **Escalation (60s):** Rohan fails through the full ladder, types distress + answer-demand. Risk panel crosses threshold; escalation card appears live on the dashboard with trigger + excerpt. Contrast: Maya also failed twice and once said "this is hard" — suppressed near-escalation log shown. "In 12 scripted sessions, escalation precision was 5/6." *Escalation precision.*
8. **Close (45s):** Eval evidence screen — DeepEval table, Ragas faithfulness, Phoenix trace of the exact turn a judge asks about. Optional: upload a decimals curriculum doc → generated concept graph appears in the review queue → approve → new subject live.

**Contingencies:** pre-record the escalation beat as a GIF fallback; keep a seeded DB snapshot for instant reset; never demo on an empty database.

## 13. Pedagogy grounding (why judges should believe us)

- **Error triage** is classic ITS research: slips vs "buggy rules" (systematic misconceptions) vs missing prerequisites. Bayesian Knowledge Tracing (Corbett & Anderson, 1995 — the model behind Carnegie Learning's Cognitive Tutor) encodes "don't overreact to one mistake" as slip/guess probabilities.
- **Prerequisite graphs** are the backbone of ALEKS (Knowledge Space Theory): teach from the "outer fringe" — concepts whose prerequisites are mastered.
- **Hint ladders** (point → teach → bottom-out) are the Cognitive Tutor pattern; "gaming the system" research (rapid hint-clicking) is why the ladder is code-enforced and hint-spam feeds the cheating signal.
- **Spaced repetition** (Leitner/SM-2) and the ~70–85% success sweet spot for adaptive difficulty are standard; Duolingo and Khan Academy ship variants.
- **Whole-number bias** ("1/3 > 1/2 because 3 > 2") is the most documented misconception in math education — the problem statement's own example, and our seed content is built from the classics.

## 14. Build plan

| # | Phase | Deliverables |
|---|---|---|
| 1 | **Foundations** | Auth (register/login, bcrypt, JWT, role guards) · multi-subject Postgres schema + Alembic migrations · fractions concept DAG + misconception taxonomy + tagged question bank · curriculum ingestion → pgvector index |
| 2 | **Core loop** | LangGraph graph end-to-end: diagnose → classify → plan → practice → evaluate → memory write · RAG-grounded hints/worked examples · hint ladder + leakage checker · escalation gate |
| 3 | **Product surfaces** | Student UI (login, chat, quiz, plan panel, memory panel, revision plan) · teacher dashboard (roster, profiles, escalations, learning gain, curriculum upload + graph review/approval) |
| 4 | **Evidence + demo** | Pre/post seeding for 2-session students · DeepEval/Ragas suites + Phoenix traces · red-team run · second subject generated via the pipeline · rehearsed demo script |

**Team split (4):** ① auth + API + database, ② orchestrator + classifier + guardrails, ③ both UIs, ④ content + RAG + graph generator + evals/demo.

**Risks:**
- **Sequencing:** generalize only after the fractions loop is green end-to-end; auth and RAG ingestion parallelize safely, the graph generator lands last.
- **Auto-generated graph quality:** mitigated by the validation checks + mandatory teacher approval gate.
- **RAG retrieval quality:** mitigated by metadata-filtered retrieval and Ragas thresholds; fall back to the curated question bank if retrieval underperforms.
- **Demo flakiness:** seeded DB snapshot, pre-recorded fallback for the escalation beat, never demo on an empty database.
