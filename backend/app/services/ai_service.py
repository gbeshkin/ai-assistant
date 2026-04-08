from langdetect import detect
from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.prompts import SYSTEM_PROMPT
from app.services.city_policy import find_topic, get_topic_hint

client = OpenAI(api_key=OPENAI_API_KEY)


def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang.startswith("ru"):
            return "ru"
        if lang.startswith("et"):
            return "et"
        return "en"
    except Exception:
        return "en"


def generate_answer(question: str) -> tuple[str, str, str | None]:
    language = detect_language(question)
    topic_id = find_topic(question)
    topic_hint = get_topic_hint(topic_id)

    language_instruction = {
        "ru": "Answer in Russian.",
        "et": "Answer in Estonian.",
        "en": "Answer in English.",
    }[language]

    user_prompt = f"""
User question:
{question}

Topic guidance:
{topic_hint}

Additional instruction:
{language_instruction}
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = response.output_text.strip()
    return answer, language, topic_id
