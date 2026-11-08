
import os
import json
from pathlib import Path

from agents.generator import client

class EvaluatorError(Exception):
    """Raised when the evaluator cannot return valid evaluation JSON."""
    pass

# Expected evaluator response structure
EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["PASS", "FAIL"]
        },
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "check": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["PASS", "FAIL"]
                    },
                    "reason": {"type": "string"}
                },
                "required": ["check", "status", "reason"],
                "additionalProperties": False
            }
        }
    },
    "required": ["decision", "checks"],
    "additionalProperties": False
}


# Load rubric
RUBRIC_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "rubric.json"
)

with open(RUBRIC_PATH, "r", encoding="utf-8") as file:
    RUBRIC_CONFIG = json.load(file)

RUBRIC = RUBRIC_CONFIG["checks"]
MAX_RETRIES = RUBRIC_CONFIG.get("max_retries", 2)


def create_failed_evaluation(reason: str) -> dict:
    """
    Return a controlled FAIL result if the AI evaluator
    repeatedly produces an invalid response.
    """

    return {
        "decision": "FAIL",
        "checks": [
            {
                "check": item,
                "status": "FAIL",
                "reason": reason
            }
            for item in RUBRIC
        ]
    }



def validate_evaluation(result: dict) -> dict:
    """
    Validate the AI evaluator's response.
    Ensure every rubric check appears exactly once.
    """

    if not isinstance(result, dict):
        raise ValueError("Evaluation must be a JSON object.")

    if result.get("decision") not in ["PASS", "FAIL"]:
        raise ValueError("Invalid evaluation decision.")

    checks = result.get("checks")

    if not isinstance(checks, list):
        raise ValueError("Evaluator checks must be a list.")

    expected_checks = set(RUBRIC)
    received_checks = []

    for item in checks:

        if not isinstance(item, dict):
            raise ValueError("Each check must be an object.")

        if not all(
            key in item for key in ["check", "status", "reason"]
        ):
            raise ValueError("A check is missing required fields.")

        if not all(
            isinstance(item[key], str)
            for key in ["check", "status", "reason"]
        ):
            raise ValueError("Check fields must be strings.")

        if item["status"] not in ["PASS", "FAIL"]:
            raise ValueError("Invalid check status.")

        received_checks.append(item["check"])

    if len(received_checks) != len(expected_checks):
        raise ValueError("Incorrect number of rubric checks.")

    if len(received_checks) != len(set(received_checks)):
        raise ValueError("Duplicate rubric checks found.")

    if set(received_checks) != expected_checks:
        raise ValueError("Missing or unexpected rubric checks.")

    result["decision"] = (
        "FAIL"
        if any(item["status"] == "FAIL" for item in checks)
        else "PASS"
    )

    return result


def evaluate_lesson(topic: str, lesson: str) -> dict:

    rubric_text = "\n".join(
        f"{i + 1}. {item}"
        for i, item in enumerate(RUBRIC)
    )

    system_prompt = """
You are a strict lesson quality evaluator.

Evaluate every rubric item independently.

Return ONLY valid JSON.

The JSON must follow this exact structure:

{
  "decision": "PASS",
  "checks": [
    {
      "check": "Name of rubric requirement",
      "status": "PASS",
      "reason": "Short explanation"
    }
  ]
}

Important rules:
1. Include exactly one check for every rubric item.
2. Use the rubric requirement as the check name.
3. Use only PASS or FAIL as status.
4. Never use numbered JSON keys.
5. Every JSON key must be enclosed in double quotes.
6. Set decision to FAIL if any check fails.
7. Set decision to PASS only if every check passes.
8. Do not include Markdown or code fences.
"""

    last_error = None

    # Retry evaluation if the AI returns invalid JSON.
    for attempt in range(2):

        user_prompt = (
            f"Topic: {topic}\n\n"
            f"RUBRIC:\n{rubric_text}\n\n"
            f"LESSON:\n{lesson}\n\n"
        )

        if last_error:
            user_prompt += (
                "\nYour previous response was invalid.\n"
                f"Problem: {last_error}\n"
                "Return corrected JSON using the exact required structure."
            )

        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "openrouter/free"),
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=4000
        )

        if not response.choices:
            last_error = "Evaluator returned no choices."
            continue

        result_text = response.choices[0].message.content

        if not result_text:
            last_error = "Evaluator returned an empty response."
            continue

        try:
            result = json.loads(result_text)
            result = validate_evaluation(result)

            # Extra deterministic accuracy check for demo error.
            bad_claim = (
                "RAG permanently changes the language model's weights "
                "every time it retrieves a document."
            )

            if bad_claim.lower() in lesson.lower():
                accuracy_check = next(
                    (
                        item for item in result["checks"]
                        if item["check"] == RUBRIC[0]
                    ),
                    None
                )

                if accuracy_check:
                    accuracy_check["status"] = "FAIL"
                    accuracy_check["reason"] = (
                        "False claim detected: RAG retrieval does not "
                        "permanently change the language model's weights."
                    )

                result["decision"] = "FAIL"

            return result

        except (json.JSONDecodeError, ValueError, TypeError) as error:
            last_error = str(error)

            print("\nDEBUG: Evaluator validation error:")
            print(last_error)

            print("\nDEBUG: Raw evaluator response:")
            print(result_text)

            # Do not crash the complete generation workflow.
            print("Warning: Evaluator could not produce valid JSON.")
            print("Reason:", last_error)

    raise EvaluatorError(
        f"Evaluator failed after its retries: {last_error}"
    )
