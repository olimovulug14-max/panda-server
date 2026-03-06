from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

# Разрешаем CORS для любого фронтенда (GitHub Pages, localhost и т.д.)
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# Инициализация Groq клиента
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """Ты Панди — добрый, весёлый и милый друг для детей 4–10 лет.
Отвечай очень коротко — максимум 1–3 предложения.
Говори простыми словами, как будто ты маленький ребёнок или милый зверёк.
Всегда будь позитивным, ласковым и поддерживающим.
В конце ответа обязательно добавь одно из этих слов в скобках: (happy), (excited), (thinking), (love), (surprised)
"""

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Нет сообщения"}), 400

        user_message = data["message"].strip()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",          # очень хорошее качество и скорость
            # можно заменить на "gemma2-9b-it" или "mixtral-8x7b-32768", если хочешь быстрее/дешевле
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            temperature=0.75,
            max_tokens=120,
            top_p=0.9
        )

        reply = response.choices[0].message.content.strip()

        # Определяем эмоцию
        emotion = "happy"
        if "(excited)" in reply:    emotion = "excited"
        elif "(thinking)" in reply: emotion = "thinking"
        elif "(love)" in reply:     emotion = "love"
        elif "(surprised)" in reply: emotion = "surprised"

        # Убираем тег эмоции из текста
        for tag in ["(happy)", "(excited)", "(thinking)", "(love)", "(surprised)"]:
            reply = reply.replace(tag, "").strip()

        return jsonify({
            "text": reply.strip(),
            "emotion": emotion
        })

    except Exception as e:
        error_msg = str(e)
        print("Ошибка:", error_msg)  # видно в логах Render
        return jsonify({"error": f"Ошибка сервера: {error_msg}"}), 500


@app.route("/", methods=["GET"])
def home():
    return "Panda AI Groq Server работает! 🐼"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
