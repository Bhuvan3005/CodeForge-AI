import json
import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.1-8b-instant"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def _clean_json(text: str) -> str:
    """
    Remove markdown fences from LLM output.
    """

    text = text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]

    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()


async def call_llm_json(
    prompt: str,
    temperature: float = 0.3,
):
    """
    Call Groq and return parsed JSON.

    Every mentor node uses this helper.
    """

    try:

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temperature,
        )

        text = _clean_json(
            response.choices[0].message.content
        )

        print("=" * 80)
        print(text)
        print("=" * 80)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.error("LLM returned invalid JSON:")
            logger.error(text)
            return None

    except Exception:

        logger.exception(
            "Groq JSON parsing failed."
        )

        return None