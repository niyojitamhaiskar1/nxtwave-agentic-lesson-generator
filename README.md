
# Self-Evaluating AI Lesson Generator

A Python-based AI lesson generation system using OpenRouter API. It creates beginner-friendly lessons, evaluates them against a strict binary rubric, regenerates failed lessons (maximum two retries), and maintains rejection history with persistent improvement memory.

## Architecture

- **Generator**: creates a standalone Markdown lesson for a beginner.
- **Evaluator**: checks every rubric checkpoint and returns structured PASS/FAIL results.
- **Controller (`main.py`)**: manages generation, evaluation, feedback, and the retry limit.
- **Persistent memory**: stores repeated failures and turns them into future prompt-improvement rules.

## Requirements

- Python 3.10+
- OpenRouter API key and API access
- Internet connection for API calls

## Setup

```bash
python -m venv .venv
```

Activate it:

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a .env file using .env.example as a template.

Add your OpenRouter API key and the required configuration.

Important: Never upload your .env file or share your API key publicly.

## Run
Generate a lesson:
```bash
python main.py --topic "Introduction to RAG"
```

To demonstrate evaluator rejection, inject a known false statement into the first draft:

```bash
python main.py --topic "Introduction to RAG" --demo-error
```

The demo fault is deliberately added only to the first draft. The evaluator should reject it, send feedback to the generator, and attempt a correction.

## Outputs

- `outputs/final_lesson.md`: saved only after all checks pass.
- `outputs/rejection_log.json`: stores failed attempts, reasons, and requested changes.
- `outputs/last_evaluation.json`: stores the final structured evaluation.
- `memory/failure_memory.json`: stores persistent failure counts and learned improvement rules.

## Design decisions and trade-offs

1. Python orchestration makes the state transitions and retry limit explicit and easy to inspect.
2. Structured Outputs constrain evaluator responses to a known JSON schema.
3. The rubric is binary: all checks must pass; there is no average score that can hide a critical failure.
4. The maximum of two retries prevents an endless loop and controls API cost.
5. JSON memory is simple and transparent for a small assignment. SQLite would be a better next step for concurrent runs and larger histories.
6. An LLM evaluator can still make mistakes. The demo includes a deterministic guard for its known injected false claim; production use should add source-based factual checks and human review for high-impact lessons.

## Important

This is an assignment prototype, not a guarantee of factual correctness. Review the final lesson and logs before submission. The AI models can be configured through the model settings in `agents/generator.py` and `agents/evaluator.py`, depending on model availability through OpenRouter.
