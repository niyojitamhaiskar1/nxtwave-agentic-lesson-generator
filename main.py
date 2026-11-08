
import argparse
from pathlib import Path
from agents.generator import generate_lesson
from agents.evaluator import evaluate_lesson, EvaluatorError
from memory.store import load_memory, save_memory, learn_from_failures
from utils.io import save_text, save_json

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
MAX_RETRIES = 2

def main():
    parser = argparse.ArgumentParser(description="Self-evaluating beginner lesson generator")
    parser.add_argument("--topic", default="Introduction to RAG", help="Topic to teach")
    parser.add_argument("--demo-error", action="store_true",
                        help="Inject a deliberately incorrect claim to demonstrate evaluator rejection")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    memory = load_memory()
    feedback = []
    rejection_log = []
    lesson = ""

    for attempt in range(MAX_RETRIES + 1):
        print(f"\n=== Generation attempt {attempt + 1} ===")
        lesson = generate_lesson(args.topic, feedback, memory["improvement_rules"])

        # Demo-only fault injection: deliberately corrupt the first draft.
        if args.demo_error and attempt == 0:
            lesson += (
                "\n\n## Deliberate test statement\n"
                "RAG permanently changes the language model's weights every time it retrieves a document.\n"
            )

        try:
            evaluation = evaluate_lesson(args.topic, lesson)
        except EvaluatorError as error:
            print("\nEVALUATION ERROR:", error)

            save_text(
                OUTPUT_DIR / "unevaluated_lesson.md",
                lesson
            )

            save_json(
                OUTPUT_DIR / "evaluation_error.json",
                {
                    "attempt": attempt + 1,
                    "status": "EVALUATION_ERROR",
                    "reason": str(error)
                }
            )

            print(
                "\nSTOP: The lesson could not be evaluated. "
                "It has NOT been marked as a content failure."
            )

            return
        print(f"Decision: {evaluation['decision']}")

        failed = [item for item in evaluation["checks"] if item["status"] == "FAIL"]
        if not failed:
            save_text(OUTPUT_DIR / "final_lesson.md", lesson)
            save_json(OUTPUT_DIR / "rejection_log.json", rejection_log)
            save_json(OUTPUT_DIR / "last_evaluation.json", evaluation)
            print("\nPASS: Lesson saved to outputs/final_lesson.md")
            print(f"Rejection rounds: {len(rejection_log)}")
            return

        failure_summary = [
            {"check": item["check"], "reason": item["reason"]}
            for item in failed
        ]
        rejection_log.append({
            "attempt": attempt + 1,
            "decision": "REJECTED",
            "failed_checks": failure_summary,
            "change_requested": "Revise only the failed areas; preserve correct explanations."
        })
        feedback = failure_summary
        learn_from_failures(memory, failed)
        save_memory(memory)
        print("Failed checks:")
        for item in failed:
            print(f"- {item['check']}: {item['reason']}")

    save_text(OUTPUT_DIR / "last_rejected_lesson.md", lesson)
    save_json(OUTPUT_DIR / "rejection_log.json", rejection_log)
    print("\nSTOP: Maximum retries reached. No lesson was approved.")

if __name__ == "__main__":
    main()
