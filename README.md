# 🤝 Collaborating AI Assistants — Multi-Agent Coder/Tester Team

A beginner-friendly, portfolio-ready project where two AI agents work
together like a real dev team: a **Coder** writes a solution, a
**Tester** writes and runs tests against it, and if it fails, the
Tester reports the bug back so the Coder can fix it — automatically,
in a loop. A **human approval gate** stops the system from ever running
AI-written code without your permission.

Built for **Project 2** of the Beginner AI Engineer Portfolio Roadmap.

---

## ✨ Features

| Feature | What it does |
|---|---|
| **Team Communication** | Coder and Tester agents pass code, tests, and bug reports back and forth |
| **Ask the Human (HITL)** | Pauses before running any code and waits for you to approve it |
| **Self-Fixing Loop** | If tests fail, the Tester diagnoses the bug and the Coder retries — up to a set number of attempts |
| **Sandboxed execution** | All AI-generated code runs inside an isolated, network-disabled Docker container — never directly on your machine |

## 🧱 Tech Stack

- **LangGraph** — orchestrates the multi-agent workflow as a state machine
- **Groq API (free tier)** — powers both the Coder and Tester agents, very fast
- **Docker** — safely executes AI-generated code in an isolated sandbox

## 📁 Project Structure

```
multi-agent-coder-tester/
├── requirements.txt
├── .env.example
├── .gitignore
├── generated/                # final approved solution + tests land here
└── src/
    ├── config.py               # all settings in one place
    ├── agents.py                # Coder agent + Tester agent (LLM prompts)
    ├── sandbox.py                # runs code safely inside Docker
    ├── graph.py                  # LangGraph workflow: coder <-> tester <-> human
    └── main.py                    # CLI entry point
```

---

## 🚀 Setup Instructions

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/<your-username>/multi-agent-coder-tester.git
cd multi-agent-coder-tester
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt --no-cache-dir
```

### 3. Make sure Docker is running

This project uses Docker to run AI-generated code safely, isolated from
your real machine (no internet access inside the container, read-only
code mount, memory limit). Start Docker Desktop, then pull the sandbox
image once:

```bash
docker pull python:3.11-slim
```

### 4. Get a free Groq API key

1. Go to https://console.groq.com/keys
2. Sign up (free, no credit card needed)
3. Click "Create API Key" and copy it

### 5. Set up your `.env` file

```bash
cp .env.example .env
```

Open `.env` and paste your key:
```
GROQ_API_KEY=gsk_your_real_key_here
```

### 6. Run it

```bash
python -m src.main "write a function that checks if a number is prime"
```

Or run it without arguments and it'll ask you for a task:
```bash
python -m src.main
```

You'll see the Coder write code, then a prompt asking you to approve
running it. Type `y` and watch the Tester write tests, run them in
Docker, and — if they fail — explain the bug so the Coder can fix it.

---

## 🧪 Try these example tasks

```bash
python -m src.main "write a function that reverses a linked list"
python -m src.main "write a function that checks if a string is a valid palindrome, ignoring spaces and punctuation"
python -m src.main "write a function that merges two sorted lists into one sorted list"
```

---

## 🐙 Maintaining This on GitHub

### First time pushing this project

```bash
cd multi-agent-coder-tester
git init
git add .
git commit -m "Initial commit: multi-agent coder/tester team (Project 2)"
git branch -M main
git remote add origin https://github.com/<your-username>/multi-agent-coder-tester.git
git push -u origin main
```

> ⚠️ **Never commit your `.env` file** — it contains your real API key.
> The included `.gitignore` already excludes it.

### Day-to-day workflow

```bash
git add .
git commit -m "Describe what you changed"
git push
```

### Suggested commit milestones (good for your portfolio's history!)

1. `Initial commit: project scaffold`
2. `Add Coder and Tester agent prompts`
3. `Add Docker sandbox for safe execution`
4. `Add LangGraph workflow with human approval gate`
5. `Add self-fixing retry loop`
6. `Add README and setup docs`

---

## 🔧 Ideas to Extend Further

- Swap the `input()` approval gate for a small web UI (Streamlit) with an "Approve" button
- Add a third agent: a "Reviewer" that checks code style/readability before testing
- Log every attempt (code, tests, feedback) to a file for a full audit trail
- Support multi-file solutions instead of a single `solution.py`
- Add a max-cost/max-token budget so a stuck loop can't run forever

---

## 📝 License

MIT — feel free to use this as a learning project or portfolio piece.
