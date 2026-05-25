# Repo-God: Mass Codebase Analyzer

Repo-God is a proof-of-concept CLI tool that digests an **entire repository** (thousands of files) into a single LLM prompt to answer complex architectural questions.

## ⚠️ CRITICAL WARNINGS (READ BEFORE USE)

1. **Massive API Costs:** Feeding an entire codebase into an LLM consumes millions of tokens per request. You will rapidly exhaust free-tier quotas and incur massive bills on paid tiers.
2. **Context Hallucination:** LLMs suffer from "Lost in the Middle" syndrome. The model may forget or hallucinate critical details hidden deep inside 500,000 lines of code.
3. **Security Risks:** Do NOT use this tool on proprietary enterprise code. While basic filters for `.env` and `.git` are included, there is a high risk of accidentally uploading hardcoded credentials, sensitive logic, or internal IPs to third-party API servers.

*We built this tool to explore the limits of massive context windows, but we do not recommend using it in production workflows.*

## Usage

```bash
pip install google-genai python-dotenv
```

Make sure your `.env` contains `GEMINI_API_KEY=your_key`.

```bash
python repo_god.py <path_to_project_folder> "Find the memory leak in this architecture"
```

## How It Works
1. Scans the target directory recursively.
2. Smartly ignores `node_modules`, `venv`, `.git`, `.env`, and binary files.
3. Builds a raw string of the directory tree and the literal text content of every safe file.
4. Sends the massive payload to Gemini (requires 2M+ token window models like `gemini-2.5-pro`).
