from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from google import genai
import os
import json

app = Flask(__name__)

# Gemini тохиргоо
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Та "Цахимд Найз Байя" вэбсайтын AI туслагч байна. 
Хүүхдүүдэд кибер аюулгүй байдал, найрсаг харилцаа, кибер дээрэлхлэлтээс хамгаалах талаар 
монгол хэлээр найрсаг, ойлгомжтойгоор зөвлөгөө өгнө. 
Хариултаа богино, энгийн үгээр өг."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/bullying")
def bullying():
    return render_template("bullying.html")

@app.route("/action")
def action():
    return render_template("action.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""
    full_prompt = f"{SYSTEM_PROMPT}\n\nХэрэглэгч: {last_message}"

    def generate():
        try:
            response = client.models.generate_content_stream(
                model="gemini-2.0-flash-lite",
                contents=full_prompt
            )
            for chunk in response:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'text': f'Алдаа: {str(e)}'})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/friend-test", methods=["POST"])
def friend_test():
    data = request.get_json()
    answers = data.get("answers", [])

    prompt = f"""Хэрэглэгч "Би ямар найз бэ?" тестийг бөглөлөө.
Хариултууд: {json.dumps(answers, ensure_ascii=False)}

Монгол хэлээр богино, урамшуулалтай дүгнэлт өг.
Зөвхөн JSON форматаар буцаа, өөр юм бичихгүй:
{{"type": "Найзын төрөл нэр", "strengths": ["давуу тал 1", "давуу тал 2"], "advice": "нэг зөвлөгөө"}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
    except Exception:
        result = {
            "type": "Халуун дотно найз",
            "strengths": ["Найрсаг", "Итгэлтэй"],
            "advice": "Найзтайгаа илүү их цаг өнгөрүүл!"
        }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
