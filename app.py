from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

<<<<<<< HEAD
app = Flask(__name__)

# Estado em memória por usuário
user_states = {}

CRITERIOS = [
    ("estrutura", "1/7 - Estrutura do sistema: dê uma nota de 0 a 10.\n0 = totalmente fechada/dogmática\n10 = muito aberta ao questionamento"),
    ("controle", "2/7 - Mecanismo de controle: dê uma nota de 0 a 10.\n0 = medo/culpa muito fortes\n10 = adesão livre, sem coerção"),
    ("filosofia", "3/7 - Base filosófica: dê uma nota de 0 a 10.\n0 = muito contraditória\n10 = muito coerente"),
    ("psicologico", "4/7 - Impacto psicológico: dê uma nota de 0 a 10.\n0 = piora culpa/ansiedade\n10 = favorece equilíbrio e paz"),
    ("social", "5/7 - Impacto social: dê uma nota de 0 a 10.\n0 = gera intolerância/opressão\n10 = promove cooperação e respeito"),
    ("liberdade", "6/7 - Liberdade individual: dê uma nota de 0 a 10.\n0 = quase nenhuma liberdade\n10 = alta liberdade para discordar/sair"),
    ("aplicabilidade", "7/7 - Aplicabilidade prática: dê uma nota de 0 a 10.\n0 = não ajuda em nada\n10 = muito útil na vida real"),
]

MANIPULACAO = [
    ("intermediario", "Teste de manipulação 1/4: precisa de intermediário obrigatório (líder, clero, guru) para tudo?\nResponda: sim ou nao"),
    ("medo", "Teste de manipulação 2/4: usa medo como ferramenta principal?\nResponda: sim ou nao"),
    ("questionamento", "Teste de manipulação 3/4: desencoraja questionamento?\nResponda: sim ou nao"),
    ("exclusividade", "Teste de manipulação 4/4: promete recompensa/salvação exclusiva?\nResponda: sim ou nao"),
]

def nova_sessao():
    return {
        "step": "aguardando_nome",
        "tradicao": "",
        "notas": {},
        "flags": {},
        "criterio_idx": 0,
        "flag_idx": 0,
    }

def interpretar_total(total):
    if total >= 60:
        return "Sistema relativamente equilibrado"
    elif total >= 40:
        return "Sistema que exige cautela e análise crítica"
    else:
        return "Sistema com forte tendência a controle, inconsistência ou opressão"

def interpretar_risco(flags_marcadas):
    if flags_marcadas >= 3:
        return "Alto risco de manipulação"
    elif flags_marcadas == 2:
        return "Risco moderado de manipulação"
    else:
        return "Baixo risco de manipulação"

def montar_resultado(state):
    total = sum(state["notas"].values())
    flags_marcadas = sum(1 for v in state["flags"].values() if v)

    linhas = [
        f"Religião/tradição analisada: {state['tradicao']}",
        "",
        "Notas FAR:",
        f"- Estrutura: {state['notas'].get('estrutura', 0)}",
        f"- Controle: {state['notas'].get('controle', 0)}",
        f"- Filosofia: {state['notas'].get('filosofia', 0)}",
        f"- Psicológico: {state['notas'].get('psicologico', 0)}",
        f"- Social: {state['notas'].get('social', 0)}",
        f"- Liberdade: {state['notas'].get('liberdade', 0)}",
        f"- Aplicabilidade: {state['notas'].get('aplicabilidade', 0)}",
        "",
        f"Pontuação total: {total}/70",
        f"Leitura geral: {interpretar_total(total)}",
        "",
        f"Flags de manipulação marcadas: {flags_marcadas}/4",
        f"Risco de manipulação: {interpretar_risco(flags_marcadas)}",
        "",
    ]

    if flags_marcadas >= 3:
        linhas.append("Conclusão: há sinais fortes de medo, coerção ou exclusividade.")
    elif total >= 60 and flags_marcadas <= 1:
        linhas.append("Conclusão: há mais indícios de sistema aberto e funcional do que de controle.")
    else:
        linhas.append("Conclusão: a análise ficou intermediária; vale aprofundar com exemplos concretos.")

    linhas.append("")
    linhas.append("Comandos: iniciar | reset | resumo")
    return "\n".join(linhas)

@app.route("/")
def home():
    return "Bot FAR online."
=======
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
>>>>>>> 0ddefa4b4a85cece01bb40f48298310fb4a8a7e3

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip().lower()
    user = request.values.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    if user not in user_states:
<<<<<<< HEAD
        user_states[user] = nova_sessao()

    state = user_states[user]

    if incoming_msg in ["reset", "reiniciar"]:
        user_states[user] = nova_sessao()
        msg.body("Sessão reiniciada.\n\nDigite o nome da religião, tradição ou grupo que você quer analisar.")
        return str(resp)

    if incoming_msg == "iniciar":
        user_states[user] = nova_sessao()
        msg.body("FAR - Framework de Análise de Religiões\n\nDigite o nome da religião, tradição ou grupo que você quer analisar.")
        return str(resp)

    if incoming_msg == "resumo":
        if state["tradicao"] and state["notas"]:
            msg.body(montar_resultado(state))
        else:
            msg.body("Ainda não há dados suficientes. Digite iniciar para começar.")
        return str(resp)

    if state["step"] == "aguardando_nome":
        if not incoming_msg:
            msg.body("Digite o nome da religião, tradição ou grupo que você quer analisar.")
            return str(resp)

        state["tradicao"] = request.values.get("Body", "").strip()
        state["step"] = "notas"
        _, pergunta = CRITERIOS[0]
        msg.body(f"Analisando: {state['tradicao']}\n\n{pergunta}")
        return str(resp)

    if state["step"] == "notas":
        try:
            nota = int(incoming_msg)
        except ValueError:
            msg.body("Resposta inválida. Envie apenas um número inteiro de 0 a 10.")
            return str(resp)

        if nota < 0 or nota > 10:
            msg.body("A nota deve estar entre 0 e 10.")
            return str(resp)

        chave, _ = CRITERIOS[state["criterio_idx"]]
        state["notas"][chave] = nota
        state["criterio_idx"] += 1

        if state["criterio_idx"] < len(CRITERIOS):
            _, pergunta = CRITERIOS[state["criterio_idx"]]
            msg.body(pergunta)
        else:
            state["step"] = "flags"
            _, pergunta = MANIPULACAO[0]
            msg.body("Agora vamos ao teste de manipulação.\n\n" + pergunta)
        return str(resp)

    if state["step"] == "flags":
        if incoming_msg not in ["sim", "nao", "não"]:
            msg.body("Resposta inválida. Responda apenas com sim ou nao.")
            return str(resp)

        valor = incoming_msg == "sim"
        chave, _ = MANIPULACAO[state["flag_idx"]]
        state["flags"][chave] = valor
        state["flag_idx"] += 1

        if state["flag_idx"] < len(MANIPULACAO):
            _, pergunta = MANIPULACAO[state["flag_idx"]]
            msg.body(pergunta)
        else:
            state["step"] = "finalizado"
            msg.body(montar_resultado(state))
        return str(resp)

    if state["step"] == "finalizado":
        msg.body("Essa análise já foi concluída.\n\nDigite iniciar para uma nova análise ou resumo para ver o resultado novamente.")
        return str(resp)

    msg.body("Digite iniciar para começar.")
=======
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

>>>>>>> 0ddefa4b4a85cece01bb40f48298310fb4a8a7e3
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
