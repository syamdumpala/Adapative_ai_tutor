# Using the Local LLM (DSLAB Ollama)

Run the tutor backend on a **free, local LLM** hosted on the lab GPU box (DSLAB,
`172.18.40.101`, NVIDIA RTX A5000). It exposes an **OpenAI-compatible** endpoint,
so the app talks to it exactly like any OpenAI/Anthropic API — no code changes,
no API tokens spent.

You connect over an **SSH tunnel** that forwards your machine's `localhost:11434`
to the lab's Ollama server. The model server is already running on the box; you
only need to tunnel in and flip four env vars.

> **Access:** you need the shared `teaching` SSH account for `172.18.40.101`.
> Get the credentials from the team over a private channel — they are **not** in
> this repo.

---

## 1. Open the SSH tunnel (leave it running)

Forwards *your* `localhost:11434` → the lab's Ollama. Enter the password when
prompted.

**Mac / Linux** (backgrounds itself):
```bash
ssh -fN -o ServerAliveInterval=60 -L 11434:localhost:11434 teaching@172.18.40.101
```

**Windows** (PowerShell — keep this window open/minimized):
```powershell
ssh -N -L 11434:localhost:11434 teaching@172.18.40.101
```

> If `ssh` isn't found on Windows: **Settings → Apps → Optional Features → add
> "OpenSSH Client"** (built into Windows 10 1809+ and Windows 11).

To close the tunnel later:
- Mac / Linux: `pkill -f "11434:localhost:11434"`
- Windows: close the PowerShell window.

---

## 2. Verify the tunnel

You should see `qwen2.5-7b-32k` in the model list.

**Mac / Linux:**
```bash
curl -s http://localhost:11434/v1/models
```

**Windows (PowerShell):**
```powershell
curl.exe http://localhost:11434/v1/models
```

---

## 3. Point the backend at the local model

In `backend/.env`, set these four lines (comment out any `LLM_PROVIDER=anthropic`):

```env
LLM_PROVIDER=local
LOCAL_BASE_URL=http://localhost:11434/v1
LOCAL_API_KEY=ollama
LLM_MODEL=qwen2.5-7b-32k:latest
```

The backend's `local` provider (`app/core/llm.py`) reuses the OpenAI client with
`base_url` pointed at the tunnel — this is a **config change only**.

---

## 4. Run the backend

```bash
cd backend
make run
```

Then drive a tutoring session via the frontend or `POST /tutor/ask`.

---

## Use it in any other code (optional)

Because it's an OpenAI-compatible endpoint, any OpenAI client works — just set
`base_url` and a placeholder key:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
print(client.chat.completions.create(
    model="qwen2.5-7b-32k:latest",
    messages=[{"role": "user", "content": "hello"}],
).choices[0].message.content)
```

---

## Available models

`qwen2.5-7b-32k` is the recommended default for the tutor. Others on the box
(run `ollama list` there to see all) include:

| Model                    | Notes                                  |
| ------------------------ | -------------------------------------- |
| `qwen2.5-7b-32k:latest`  | **Default** — strong reasoning, 32k ctx |
| `llama3.1-8b-32k:latest` | Lighter alternative                    |
| `glm-4.7-flash-32k:latest` | Heavier, more capable                |
| `nomic-embed-text:latest`| Embeddings (for memory / RAG)          |

Change `LLM_MODEL` to switch. The name must match a tag from `ollama list`.

---

## Troubleshooting

- **App can't reach the model / connection refused** → the tunnel dropped. It
  dies on window close, reboot, or logout. Re-run step 1, then re-check step 2.
- **`ssh` asks for a password every time** → normal for the shared account; set
  up an SSH key with the team if you want passwordless access.
- **Port 11434 already in use locally** → you already have a tunnel (or a local
  Ollama) running; you're good, or kill the old one first.

---

## Switching back to the Claude subscription

In `backend/.env`, comment out the four `local` lines and restore:

```env
LLM_PROVIDER=anthropic
LLM_AUTH_MODE=subscription
LLM_MODEL=claude-opus-4-8
```
