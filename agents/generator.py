
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
         "OPENROUTER_API_KEY not found. Add it to your .env file."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def generate_lesson(topic: str, feedback: list, improvement_rules: list) -> str:
    feedback_text = "\n".join(
        f"- {item['check']}: {item['reason']}" for item in feedback
    ) or "No previous evaluator feedback. Create the first draft."

    memory_text = "\n".join(
        f"- {rule}" for rule in improvement_rules
    ) or "No learned rules yet."

    instructions = """
You are a patient teacher creating a standalone beginner lesson.
Audience: an Indian 12th-grade graduate from a non-English-medium background,
with limited English vocabulary and no prior knowledge of the topic.

Use short sentences and common words. Explain every technical word the first
time it appears. Use a familiar real-life example. Teach in this order:
1. What it is
2. Why it is useful / what problem it solves
3. Key parts
4. How it works step by step
5. A worked example
6. What it cannot do / limitations
7. Short recap and 3 simple self-check questions

For RAG, explain retrieval, relevant information, context, and generation.
Be accurate: retrieving documents does not itself train or update the model's
weights. Explain that RAG can help a model answer using supplied information,
but it does not guarantee truth. Do not assume the learner knows Python,
databases, embeddings, APIs, or machine learning.
Return the lesson in Markdown only.
"""

    user_input = f"""
Topic: {topic}

Persistent improvement rules learned from earlier runs:
{memory_text}

Feedback from the previous attempt:
{feedback_text}

Create or revise the lesson. Address every failed check explicitly.
Do not mention the evaluation process in the lesson.
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "openrouter/free"),
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_input},
        ],
    )

    return response.choices[0].message.content.strip()
