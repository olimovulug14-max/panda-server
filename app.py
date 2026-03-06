from flask import Flask, request, jsonify
import os
from groq import Groq  # pip install groq

app = Flask(__name__)

# CORS
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # быстро + качество, или "gemma2-9b-it", "mixtral-8x7b-32768"
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150,
            top_p=0.9
        )

        reply = response.choices[0].message.content.strip()

        # Извлекаем эмоцию
        emotion = "happy"
        if "(excited)" in reply: emotion = "excited"
        elif "(thinking)" in reply: emotion = "thinking"
        elif "(love)" in reply: emotion = "love"
        elif "(surprised)" in reply: emotion = "surprised"

        # Убираем тег
        for tag in ["(happy)", "(excited)", "(thinking)", "(love)", "(surprised)"]:
            reply = reply.replace(tag, "").strip()

        return jsonify({"text": reply, "emotion": emotion})

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    return "Panda AI Groq Server работает! 🐼"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
