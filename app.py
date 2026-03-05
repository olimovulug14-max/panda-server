from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

app = Flask(__name__)

# CORS вручную
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# Gemini настройка
genai.configure(api_key="AIzaSyCYDLj0Hu5VwdtT4G7lME9ZrL9XZBAi-4I")
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """Ты Панди — добрый и весёлый друг для детей 4-10 лет.
- Отвечай коротко (1-3 предложения)
- Говори просто и понятно
- Всегда добрый и позитивный
- Иногда используй слова как "Вау!", "Здорово!", "Отлично!"
- В конце каждого ответа добавь одно слово в скобках: (happy), (excited), (thinking), (love), (surprised)
"""

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 200

    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Нет сообщения"}), 400

    full_prompt = SYSTEM_PROMPT + "\nРебёнок говорит: " + user_message
    response = model.generate_content(full_prompt)
    reply = response.text.strip()

    emotion = "happy"
    if "(excited)" in reply: emotion = "excited"
    elif "(thinking)" in reply: emotion = "thinking"
    elif "(love)" in reply: emotion = "love"
    elif "(surprised)" in reply: emotion = "surprised"

    clean_reply = reply
    for tag in ["(happy)","(excited)","(thinking)","(love)","(surprised)"]:
        clean_reply = clean_reply.replace(tag, "")
    clean_reply = clean_reply.strip()

    tts = gTTS(text=clean_reply, lang="ru", slow=False)
    audio_path = tempfile.mktemp(suffix=".mp3")
    tts.save(audio_path)

    return jsonify({
        "text": clean_reply,
        "emotion": emotion,
        "audio_url": f"/audio?path={audio_path}"
    })

@app.route("/audio", methods=["GET"])
def audio():
    path = request.args.get("path")
    return send_file(path, mimetype="audio/mpeg")

@app.route("/", methods=["GET"])
def home():
    return "🐼 Panda AI Server работает!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
