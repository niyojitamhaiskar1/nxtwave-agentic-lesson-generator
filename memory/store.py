
import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "failure_memory.json"


# Specific improvements for each rubric requirement
IMPROVEMENT_GUIDE = {
    "Accuracy and grounded explanation":
        "Check technical claims carefully. Avoid unsupported claims and explain what RAG cannot guarantee.",

    "Beginner-friendly language":
        "Use short sentences and simple English suitable for an Indian 12th-grade beginner. Explain difficult words immediately.",

    "Relatable worked example":
        "Include a familiar everyday example and explain each step using the example.",

    "Why the topic matters":
        "Explain the real problem this technology solves and why a learner would use it.",

    "Complete step-by-step workflow":
        "Explain the complete process in the correct order. Do not skip important preparation or processing steps.",

    "Key concepts explained":
        "Define every important technical term when it first appears. Include simple explanations of chunks, embeddings, and vector databases when relevant to RAG.",

    "Limitations and uncertainty":
        "Explain limitations clearly. Never promise that the system always produces correct answers.",

    "Coherent teaching flow":
        "Teach from basic ideas to more advanced ideas. Make each section connect naturally to the next.",

    "Standalone lesson with recap and questions":
        "Include an introduction, complete explanation, short recap, and at least three self-check questions."
}


def load_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {"failure_counts": {}, "improvement_rules": []}

    try:
        memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))

        if not isinstance(memory, dict):
            raise ValueError("Memory must be a JSON object.")

        memory.setdefault("failure_counts", {})
        memory.setdefault("improvement_rules", [])

        return memory

    except (json.JSONDecodeError, OSError, ValueError):
        return {"failure_counts": {}, "improvement_rules": []}


def save_memory(memory: dict) -> None:
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(memory, indent=2),
        encoding="utf-8"
    )


def learn_from_failures(memory: dict, failed_checks: list) -> None:
    """
    Learn only from genuine content failures.
    Ignore empty or unknown rubric names.
    """

    counts = memory.setdefault("failure_counts", {})
    rules = memory.setdefault("improvement_rules", [])

    for item in failed_checks:

        if not isinstance(item, dict):
            continue

        name = item.get("check", "").strip()

        if not name:
            continue

        # Find the matching known rubric requirement.
        matching_key = next(
            (
                key for key in IMPROVEMENT_GUIDE
                if name.startswith(key)
            ),
            None
        )

        if matching_key is None:
            continue

        counts[matching_key] = counts.get(matching_key, 0) + 1

        # Add a useful rule after the same failure happens twice.
        if counts[matching_key] >= 2:

            rule = IMPROVEMENT_GUIDE[matching_key]

            if rule not in rules:
                rules.append(rule)
