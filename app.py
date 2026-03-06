from flask import Flask, request, jsonify
from google import genai
import os

app = Flask(__name__)

# CORS для фронтенда (разрешаем все источники)
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# Инициализация клиента (ключ берётся из переменной окружения)
client = genai.Client()  # автоматически берёт GEMINI_API_KEY из env

SYSTEM_PROMPT = """Ты Панди — добрый и весёлый друг для детей 4-10 лет.
- Отвечай коротко (1-3 предложения)
- Говори просто и понятно
- Всегда добрый и позитивный
- В конце добавь одно слово в скобках: (happy), (excited), (thinking), (love), (surprised)
"""

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 200

    data = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Нет сообщения"}), 400

    try:
        # Структурированный контент: system + user
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # или "gemini-2.0-flash", "gemini-3-flash-preview" — выбирай свежий
            contents=[
                {"role": "system", "parts": [{"text": SYSTEM_PROMPT}]},
                {"role": "user",   "parts": [{"text": user_message}]}
            ]
        )

        reply = response.text.strip()

        # Извлекаем эмоцию
        emotion = "happy"
        if "(excited)" in reply: emotion = "excited"
        elif "(thinking)" in reply: emotion = "thinking"
        elif "(love)" in reply:    emotion = "love"
        elif "(surprised)" in reply: emotion = "surprised"

        # Убираем тег эмоции из текста
        for tag in ["(happy)", "(excited)", "(thinking)", "(love)", "(surprised)"]:
            reply = reply.replace(tag, "").strip()

        return jsonify({"text": reply, "emotion": emotion})

    except Exception as e:
        return jsonify({"error": f"Ошибка AI: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    return "Panda AI Server работает! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
