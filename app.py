import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

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
    return "Alice OpenRouter webhook is running"

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
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openrouter/free",
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": user_text
                        }
                    ],
                    "max_tokens": 120
                },
                timeout=3.8
            )

            r.raise_for_status()

            result = r.json()
            answer = result["choices"][0]["message"]["content"].strip()

            if len(answer) > 950:
                answer = answer[:947] + "..."

        except Exception as e:
            print("OpenRouter error:", str(e))
            answer = "Не удалось получить ответ. Попробуй ещё раз."

    return jsonify({
        "version": "1.0",
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": False
        }
    })
