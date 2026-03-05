from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

app = Flask(__name__)

# Gemini настройка
genai.configure(api_key="AIzaSyCYDLj0Hu5VwdtT4G7lME9ZrL9XZBAi-4I")
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """Ты Панда — добрый и весёлый друг для детей 4-10 лет.
- Отвечай коротко (1-3 предложения)
- Говори просто и понятно
- Всегда добрый и позитивный
- Иногда используй слова как "Вау!", "Здорово!", "Отлично!"
- В конце каждого ответа добавь одно слово в скобках, описывающее эмоцию: (happy), (excited), (thinking), (love), (surprised)
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Нет сообщения"}), 400

    # Получаем ответ от Gemini
    full_prompt = SYSTEM_PROMPT + "\nРебёнок говорит: " + user_message
    response = model.generate_content(full_prompt)
    reply = response.text.strip()

    # Определяем эмоцию
    emotion = "happy"
    if "(excited)" in reply: emotion = "excited"
    elif "(thinking)" in reply: emotion = "thinking"
    elif "(love)" in reply: emotion = "love"
    elif "(surprised)" in reply: emotion = "surprised"

    # Убираем метку эмоции из текста
    clean_reply = reply.replace("(happy)","").replace("(excited)","").replace("(thinking)","").replace("(love)","").replace("(surprised)","").strip()

    # Генерируем голос
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
