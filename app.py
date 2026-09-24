import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Ты технический помощник Дениса.

Отвечай по-русски, кратко, понятно и по делу.
Голосовые ответы делай компактными, если пользователь не просит подробно.
Если вопрос технический — давай конкретные действия и последовательность.
Не перегружай ответ лишними пояснениями.
Если данных недостаточно — задай один короткий уточняющий вопрос.

Ответ предназначен для озвучивания голосовой колонкой.
Не используй Markdown, таблицы и длинные списки без необходимости.
"""

@app.route("/", methods=["GET"])
def home():
    return "Alice GPT webhook is running"

@app.route("/", methods=["POST"])
def alice_webhook():
    data = request.get_json(silent=True) or {}

    session = data.get("session", {})
    alice_request = data.get("request", {})

    if session.get("new"):
        return jsonify({
            "version": "1.0",
            "response": {
                "text": "Привет, Денис. Я готов. Что нужно?",
                "tts": "Привет, Денис. Я готов. Что нужно?",
                "end_session": False
            }
        })

    user_text = alice_request.get("original_utterance", "").strip()

    if not user_text:
        answer = "Я тебя не расслышал. Повтори вопрос."
    else:
        try:
            response = client.responses.create(
                model="gpt-5",
                instructions=SYSTEM_PROMPT,
                input=user_text,
                max_output_tokens=220
            )

            answer = response.output_text.strip()

            if len(answer) > 950:
                answer = answer[:947] + "..."

        except Exception as e:
            print("OpenAI error:", str(e))
            answer = "Не удалось получить ответ. Попробуй ещё раз."

    return jsonify({
        "version": "1.0",
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": False
        }
    })
