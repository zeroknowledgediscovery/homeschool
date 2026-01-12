# daily_reading_test_openai.py
# Requires: pip install openai reportlab
# Env var: export OPENAI_API_KEY="..."

import os
import json
from datetime import date
from typing import Dict, Any, List

from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import textwrap


OUT_PDF = "Daily_Reading_Test_Age8.pdf"

# Choose any "daily topic" you like; script will rotate with the date
TOPIC_POOL = [
    "bees and pollination",
    "recycling and waste",
    "how sleep helps the brain",
    "why trees help cities",
    "how rivers shape land",
    "how vaccines train the immune system (kid-safe, non-scary)",
    "how magnets work",
    "why the Moon changes shape",
    "how bridges hold weight",
]

# Model selection: set to a current text-capable model in your account.
# The Responses API is OpenAI's recommended API for new projects. :contentReference[oaicite:1]{index=1}
MODEL = "gpt-5"  # if your account uses a different model name, change here.


def pick_daily_topic(today: date) -> str:
    # deterministic daily rotation
    idx = (today.year * 10000 + today.month * 100 + today.day) % len(TOPIC_POOL)
    return TOPIC_POOL[idx]


def generate_reading_test(client: OpenAI, *, topic: str, grade: str = "3-4") -> Dict[str, Any]:
    """
    Returns a dict:
      {
        "title": "...",
        "passage": "...",
        "questions": [
            {"id":"Q1","type":"multiple_choice","skill":"author_intent", ...},
            ...
        ],
        "answer_key": {"Q1":"B", "Q2":"..."}
      }
    """
    schema = {
        "name": "reading_test",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "title": {"type": "string"},
                "passage": {"type": "string"},
                "questions": {
                    "type": "array",
                    "minItems": 7,
                    "maxItems": 10,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "id": {"type": "string"},
                            "type": {"type": "string", "enum": ["multiple_choice", "short_answer"]},
                            "skill": {"type": "string", "enum": ["author_intent", "literal", "non_literal"]},
                            "prompt": {"type": "string"},
                            "choices": {
                                "type": ["array", "null"],
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["id", "type", "skill", "prompt", "choices"],
                    },
                },
                "answer_key": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["title", "passage", "questions", "answer_key"],
        },
    }

    system_instructions = (
        "You are an expert elementary reading teacher.\n"
        f"Write one short NONFICTION passage for grade {grade} readers (about 120–170 words).\n"
        "Then write 7–10 questions that test:\n"
        "1) Author's intent/purpose (at least 2 questions)\n"
        "2) Literal meaning (at least 2 questions)\n"
        "3) Non-literal/figurative meaning (at least 2 questions)\n"
        "Include at least one figurative phrase in the passage (e.g., 'a big role', 'like a mountain'), "
        "so you can test literal vs non-literal.\n"
        "Avoid scary or mature topics. Keep vocabulary and sentence length appropriate.\n"
        "Multiple choice questions should have 4 choices.\n"
        "Provide an answer key mapping question IDs to the correct choice letter (A/B/C/D) or a short expected answer."
    )

    # Responses API call :contentReference[oaicite:2]{index=2}
    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": (
                f"Topic: {topic}. Create the passage and questions.\n\n"
                "IMPORTANT: Respond with VALID JSON ONLY.\n"
                "Do not include explanations, markdown, or extra text.\n"
                "The JSON must have exactly these keys:\n"
                "{\n"
                '  "title": string,\n'
                '  "passage": string,\n'
                '  "questions": [\n'
                "     {\n"
                '       "id": string,\n'
                '       "type": "multiple_choice" | "short_answer",\n'
                '       "skill": "author_intent" | "literal" | "non_literal",\n'
                '       "prompt": string,\n'
                '       "choices": [string] | null\n'
                "     }\n"
                "  ],\n"
                '  "answer_key": { string: string }\n'
                "}\n"
            )},
        ],
    )

    raw = resp.output_text.strip()
    data = json.loads(raw)
    return data


def draw_wrapped(c: canvas.Canvas, x: float, y: float, text: str, *,
                 width_chars: int = 95, leading: int = 14,
                 font: str = "Helvetica", size: int = 11) -> float:
    c.setFont(font, size)
    for para in text.split("\n"):
        if not para.strip():
            y -= leading
            continue
        for line in textwrap.wrap(para, width=width_chars):
            c.drawString(x, y, line)
            y -= leading
        y -= leading * 0.5
    return y


def render_pdf(test: Dict[str, Any], *, out_pdf: str, today: date) -> None:
    W, H = letter
    margin = 0.7 * inch
    c = canvas.Canvas(out_pdf, pagesize=letter)
    c.setTitle("Daily Reading Test")

    today_str = today.strftime("%B %d, %Y")

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, H - margin, f"Reading Test — {today_str}")
    c.setFont("Helvetica", 11)
    c.drawString(margin, H - margin - 20, "Name: ________________________________")
    c.drawString(W - margin - 180, H - margin - 20, "Score: ______ / ______")
    c.line(margin, H - margin - 28, W - margin, H - margin - 28)

    y = H - margin - 55

    # Passage title + text
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, f"Passage: {test['title']}")
    y -= 18

    y = draw_wrapped(c, margin, y, test["passage"], width_chars=95, leading=14, font="Helvetica", size=11)
    y -= 8

    # Questions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Questions")
    y -= 16
    c.line(margin, y + 10, W - margin, y + 10)

    c.setFont("Helvetica", 11)

    for q in test["questions"]:
        prompt = q["prompt"].strip()
        y = draw_wrapped(c, margin, y, f"{q['id']}) {prompt}", width_chars=95, leading=14)

        if q["type"] == "multiple_choice" and q["choices"]:
            # Print A–D
            letters = ["A", "B", "C", "D"]
            for i, choice in enumerate(q["choices"][:4]):
                y = draw_wrapped(c, margin + 18, y, f"☐ {letters[i]}. {choice}", width_chars=92, leading=14)
            y -= 4
        else:
            # short answer lines
            c.drawString(margin, y, "   ______________________________________________")
            y -= 16
            c.drawString(margin, y, "   ______________________________________________")
            y -= 18

        # Page overflow
        if y < 1.1 * inch:
            c.showPage()
            y = H - margin
            c.setFont("Helvetica", 11)

    # Optional: print answer key on a second page (comment out if you don't want it)
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, H - margin, f"Answer Key — {today_str}")
    y = H - margin - 30
    c.setFont("Helvetica", 11)

    for q in test["questions"]:
        qid = q["id"]
        ans = test["answer_key"].get(qid, "")
        c.drawString(margin, y, f"{qid}: {ans}")
        y -= 14
        if y < 1.0 * inch:
            c.showPage()
            y = H - margin
            c.setFont("Helvetica", 11)

    c.save()

def main():
    api_key = OPENAI_API_KEY#os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY environment variable.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    today = date.today()
    topic = pick_daily_topic(today)

    test = generate_reading_test(client, topic=topic, grade="3-4")
    render_pdf(test, out_pdf=OUT_PDF, today=today)

    print(f"Wrote: {OUT_PDF}  (topic: {topic})")


if __name__ == "__main__":
    main()
