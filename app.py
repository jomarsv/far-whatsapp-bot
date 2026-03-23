from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

# IA opcional
USE_AI = os.getenv("ENABLE_AI_COMMENT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if USE_AI and OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

app = Flask(__name__)

# Estado simples (memória)
user_states = {}

questions = [
    "1️⃣ Você sente cansaço frequente? (sim/não)",
    "2️⃣ Tem dificuldade para dormir? (sim/não)",
    "3️⃣ Sente ansiedade constante? (sim/não)",
    "4️⃣ Possui dores físicas recorrentes? (sim/não)",
    "5️⃣ Se sente desmotivado frequentemente? (sim/não)",
]

def analisar_respostas(respostas):
    score = sum(1 for r in respostas if r == "sim")

    if score <= 1:
        return "🟢 Baixo risco"
    elif score <= 3:
        return "🟡 Risco moderado"
    else:
        return "🔴 Alto risco"

def gerar_comentario_ia(resultado):
    if not client:
        return ""

    try:
        resp = client.responses.create(
            model="gpt-5.4-mini",
            input=f"Gere uma explicação curta e direta para o seguinte diagnóstico: {resultado}"
        )
        return resp.output_text.strip()
    except:
        return ""

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip().lower()
    user = request.values.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    if user not in user_states:
        user_states[user] = {"step": 0, "answers": []}

    state = user_states[user]

    if incoming_msg == "iniciar":
        state["step"] = 0
        state["answers"] = []
        msg.body("👋 Vamos iniciar o diagnóstico.\n\n" + questions[0])
        return str(resp)

    if state["step"] < len(questions):
        if incoming_msg in ["sim", "não", "nao"]:
            resposta = "sim" if "sim" in incoming_msg else "não"
            state["answers"].append(resposta)
            state["step"] += 1

            if state["step"] < len(questions):
                msg.body(questions[state["step"]])
            else:
                resultado = analisar_respostas(state["answers"])
                texto = f"📊 Resultado: {resultado}"

                comentario = gerar_comentario_ia(resultado)
                if comentario:
                    texto += f"\n\n🤖 {comentario}"

                msg.body(texto)
                user_states.pop(user)
        else:
            msg.body("Responda apenas com 'sim' ou 'não'.")
    else:
        msg.body("Digite 'iniciar' para começar.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
