import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "city_topics.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    CITY_TOPICS = json.load(f)["topics"]


def find_topic(question: str) -> str | None:
    q = question.lower()
    for topic in CITY_TOPICS:
        for keyword in topic["keywords"]:
            if keyword.lower() in q:
                return topic["id"]
    return None


def get_topic_hint(topic_id: str | None) -> str:
    if not topic_id:
        return (
            "The question appears to be outside the supported demo scope. "
            "Tell the user you currently help best with parking, city services, "
            "public transport, reporting city problems, and waste/maintenance."
        )

    for topic in CITY_TOPICS:
        if topic["id"] == topic_id:
            return topic["hint"]

    return "General city demo assistance."
