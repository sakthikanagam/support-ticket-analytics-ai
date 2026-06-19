import os
import json
import google.generativeai as genai

from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

load_dotenv()

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not API_KEY:
    raise Exception(
        "GEMINI_API_KEY not found in .env file"
    )

genai.configure(
    api_key=API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def get_intent(question):

    prompt = f"""
{SYSTEM_PROMPT}

User Question:
{question}
"""

    try:

        response = model.generate_content(
            prompt
        )

        text = (
            response.text
            .strip()
        )

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        print("=" * 50)
        print("QUESTION:", question)
        print("RAW GEMINI OUTPUT:")
        print(text)
        print("=" * 50)

        plan = json.loads(
            text
        )

        return plan

    except json.JSONDecodeError:

        print(
            "Invalid JSON returned by Gemini"
        )

        return {
            "operation":
            "unsupported"
        }

    except Exception as e:

        print(
            "Gemini Error:",
            str(e)
        )

        return {
            "operation":
            "unsupported"
        }