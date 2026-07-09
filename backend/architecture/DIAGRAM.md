# Architecture Diagrams

_Last updated: 2026-07-08_

## Component overview

```mermaid
flowchart TD
    Client([Client])
    Client --> Main["app/main.py<br/>(FastAPI + lifespan)"]
    Main --> Index["app/api/router.py<br/>(route index)"]

    Index --> AuthR["features/auth/routes.py"]
    Index --> TutorR["features/tutor/routes.py"]

    AuthR --> AuthDep["auth/dependencies.py<br/>get_current_student"]
    AuthR --> AuthSvc["auth/service.py"]
    AuthSvc --> AuthModel["auth/models.py<br/>Student"]

    TutorR --> AuthDep
    TutorR --> TutorSvc["tutor/service.py"]
    TutorSvc --> Pipeline["tutor/graph/<br/>(LangGraph multi-agent)"]
    TutorSvc --> TutorModel["tutor/models.py<br/>profile · sessions · history<br/>evidence · escalations"]

    AuthSvc --> Core["core/<br/>config · database · security"]
    TutorSvc --> Core
    AuthDep --> Core
    Pipeline --> LLM["core/llm.py<br/>(provider factory)"]

    AuthModel --> DB[(PostgreSQL)]
    TutorModel --> DB
    LLM --> Providers([Claude subscription ·<br/>Anthropic · OpenAI · Gemini])
    Pipeline -.->|traces per agent| LS([LangSmith<br/>observability])
```

## Request lifecycle — POST /tutor/ask

```mermaid
sequenceDiagram
    participant C as Client
    participant R as tutor/routes.py
    participant D as get_current_student
    participant S as tutor/service.py
    participant G as graph/ (LangGraph multi-agent)
    participant DB as PostgreSQL

    C->>R: POST /tutor/ask (JWT, question, session_id?)
    R->>D: resolve current student (verify JWT)
    D-->>R: Student
    R->>R: llm_is_configured() (else 503)
    R->>S: ask_question(db, student, question, session_id)
    S->>DB: hydrate session state + append user message
    S->>G: tutor_graph.ainvoke(state)
    G-->>S: {action, output, ...} (hint / completed / escalation)
    S->>DB: persist session state, history, evidence, profile
    S-->>R: AskResponse
    R-->>C: 200 AskResponse
```

## AI graph (LangGraph multi-agent, supervisor-routed)

The supervisor re-routes after every agent based on which state fields are filled
(see `graph/router.py`). A turn ends (`END`) either after a hint is delivered
(awaiting the student's answer) or after the memory/revision or escalation branch.

```mermaid
flowchart TD
    START((START)) --> SUP{supervisor<br/>router}
    SUP -->|profile missing| PRO[Profile]
    SUP -->|diagnostic missing| DIA[Diagnostic]
    SUP -->|misconception missing| MIS[Misconception]
    SUP -->|plan missing| PLA[Planner]
    SUP -->|hint missing| HIN[Hint]
    SUP -->|answered| EVA[Evaluator]
    SUP -->|correct| MEM[Memory]
    SUP -->|distress| ESC[Escalation]
    SUP -->|hint delivered| ENDA((END: await answer))

    PRO --> SUP
    DIA --> SUP
    MIS --> SUP
    PLA --> SUP
    HIN --> GUA[Hint Guard]
    GUA --> SUP
    EVA --> SUP
    MEM --> REV[Revision Planner]
    REV --> ENDC((END: completed))
    ESC --> ENDE((END: escalated))
```

### Multi-turn loop (across API calls)

The session now opens with an **interactive Diagnostic phase**: the tutor asks 3 probing
questions (one per turn) before the first hint. The Misconception agent categorizes the
difficulty from that Q&A (`unsure_of_concept` / `misunderstanding_concept` /
`missing_prerequisite` / `none`).

```mermaid
sequenceDiagram
    participant C as Client
    participant S as service (session state)
    participant G as tutor_graph
    C->>S: POST /tutor/ask {question}
    S->>G: run -> Profile -> Diagnostic (ask probe 1)
    G-->>S: action=diagnostic (await)
    S-->>C: {session_id, probing question 1/3}
    Note over C,G: student answers probes 2/3 and 3/3 (2 more turns)
    C->>S: POST /tutor/ask {answer 3, session_id}
    S->>G: Diagnostic consolidates -> Misconception -> Planner..Hint+Guard
    G-->>S: action=hint (await)
    S-->>C: {hint}
    C->>S: POST /tutor/ask {answer, session_id}
    S->>G: resume -> Evaluator
    alt correct
        G-->>S: Memory -> Revision (completed)
        S-->>C: {completed, mastery, next_review}
    else wrong (no distress)
        G-->>S: new Hint (await)  %% unlimited hints — no attempt cap
        S-->>C: {hint}
    else distress
        G-->>S: Escalation
        S-->>C: {escalation}
    end
```

### Context & conversation

Every turn the service loads the session's `conversation_history` (all prior
student/tutor messages) plus the current student message, and passes it into the
graph as `config.configurable.history`. Each LLM agent prepends this transcript
(student → HumanMessage, tutor → AIMessage) before its task, so no agent loses
context — the Evaluator, for example, judges the latest answer against the
**initial** question using every hint in between. A subject guardrail is appended
to each agent call at runtime (prompts unchanged). Fetch the typed transcript via
`GET /tutor/sessions/{id}/conversation`; list sessions via `GET /tutor/sessions`.
