import os
import sqlite3
from contextlib import closing
from datetime import datetime
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator

APP_TITLE = "FAR Bot"
DB_PATH = os.getenv("DB_PATH", "far_bot.db")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
VALIDATE_TWILIO = os.getenv("VALIDATE_TWILIO", "false").lower() == "true"

app = Flask(__name__)

QUESTIONS = [
    ("estrutura", "De 0 a 10, qual o nível de abertura da religião para questionamento e interpretação?\n0 = totalmente fechada\n10 = muito aberta"),
    ("controle", "De 0 a 10, quanto ela usa medo, culpa ou ameaça para manter adesão?\n0 = quase nada\n10 = muito forte"),
    ("filosofia", "De 0 a 10, qual a consistência lógica e filosófica que você percebe?\n0 = muito contraditória\n10 = muito consistente"),
    ("psicologico", "De 0 a 10, qual o impacto psicológico em você?\n0 = muito negativo\n10 = muito positivo"),
    ("social", "De 0 a 10, qual o impacto social que você percebe?\n0 = muito nocivo\n10 = muito benéfico"),
    ("liberdade", "De 0 a 10, quanto de liberdade individual existe dentro dela?\n0 = quase nenhuma\n10 = muito alta"),
    ("aplicabilidade", "De 0 a 10, quanto disso é útil na vida real?\n0 = inútil\n10 = muito útil"),
]

MANIPULATION_CHECKS = [
    ("intermediario", "Precisa de intermediário obrigatório para acessar a verdade ou a salvação? Responda: sim ou nao"),
    ("medo_central", "O medo é a principal ferramenta de adesão? Responda: sim ou nao"),
    ("anti_questionamento", "Questionar é desencorajado ou punido? Responda: sim ou nao"),
    ("recompensa_exclusiva", "Ela promete recompensa exclusiva só para quem estiver dentro? Responda: sim ou nao"),
]

MENU = """
*FAR Bot – Auditoria de Religiões*\n\nEnvie um comando:\n- iniciar\n- menu\n- ajuda\n- reset\n- resumo\n\nFluxo:\n1) você informa o nome da religião\n2) responde as notas de 0 a 10\n3) responde 4 checagens de manipulação\n4) o bot entrega o diagnóstico final\n""".strip()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_db()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                phone TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                religion_name TEXT,
                question_index INTEGER DEFAULT 0,
                manipulation_index INTEGER DEFAULT 0,
                estrutura INTEGER,
                controle INTEGER,
                filosofia INTEGER,
                psicologico INTEGER,
                social INTEGER,
                liberdade INTEGER,
                aplicabilidade INTEGER,
                intermediario INTEGER DEFAULT 0,
                medo_central INTEGER DEFAULT 0,
                anti_questionamento INTEGER DEFAULT 0,
                recompensa_exclusiva INTEGER DEFAULT 0,
                updated_at TEXT
            );
            """
        )
        conn.commit()


def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds")


def get_session(phone: str):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT * FROM sessions WHERE phone = ?", (phone,)).fetchone()
        if row:
            return dict(row)
        conn.execute(
            "INSERT INTO sessions (phone, state, updated_at) VALUES (?, ?, ?)",
            (phone, "idle", now_iso()),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM sessions WHERE phone = ?", (phone,)).fetchone()
        return dict(row)


def update_session(phone: str, **fields):
    if not fields:
        return
    fields["updated_at"] = now_iso()
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    assignments = ", ".join([f"{k} = ?" for k in keys])
    with closing(get_db()) as conn:
        conn.execute(
            f"UPDATE sessions SET {assignments} WHERE phone = ?",
            (*values, phone),
        )
        conn.commit()


def reset_session(phone: str):
    update_session(
        phone,
        state="idle",
        religion_name=None,
        question_index=0,
        manipulation_index=0,
        estrutura=None,
        controle=None,
        filosofia=None,
        psicologico=None,
        social=None,
        liberdade=None,
        aplicabilidade=None,
        intermediario=0,
        medo_central=0,
        anti_questionamento=0,
        recompensa_exclusiva=0,
    )


def parse_score(text: str):
    text = text.strip().replace(",", ".")
    if not text.isdigit():
        return None
    value = int(text)
    if 0 <= value <= 10:
        return value
    return None


def parse_yes_no(text: str):
    normalized = text.strip().lower()
    yes = {"sim", "s", "yes", "y"}
    no = {"nao", "não", "n", "no"}
    if normalized in yes:
        return 1
    if normalized in no:
        return 0
    return None


def classify_total(total: int):
    if total >= 60:
        return "Sistema relativamente equilibrado"
    if total >= 40:
        return "Sistema que exige cautela e análise crítica"
    return "Sistema com forte tendência a controle, inconsistência ou dano"


def classify_manipulation(count_true: int):
    if count_true >= 3:
        return "Alto risco de manipulação"
    if count_true == 2:
        return "Risco moderado de manipulação"
    return "Baixo risco de manipulação"


def build_summary(session: dict):
    scores = {
        "Estrutura": session.get("estrutura") or 0,
        "Controle": session.get("controle") or 0,
        "Filosofia": session.get("filosofia") or 0,
        "Psicológico": session.get("psicologico") or 0,
        "Social": session.get("social") or 0,
        "Liberdade": session.get("liberdade") or 0,
        "Aplicabilidade": session.get("aplicabilidade") or 0,
    }
    total = sum(scores.values())
    manipulation_count = sum(
        int(session.get(k) or 0)
        for k in ["intermediario", "medo_central", "anti_questionamento", "recompensa_exclusiva"]
    )

    strengths = []
    weaknesses = []

    for label, value in scores.items():
        if value >= 8:
            strengths.append(label)
        elif value <= 4:
            weaknesses.append(label)

    lines = [
        f"*Diagnóstico FAR – {session.get('religion_name', 'sem nome')}*",
        "",
        "*Notas*",
    ]
    for label, value in scores.items():
        lines.append(f"- {label}: {value}/10")

    lines.extend([
        "",
        f"*Total:* {total}/70",
        f"*Leitura geral:* {classify_total(total)}",
        f"*Manipulação:* {classify_manipulation(manipulation_count)} ({manipulation_count}/4 sinais)",
        "",
        "*Pontos fortes*",
        (", ".join(strengths) if strengths else "Nenhum destaque forte"),
        "",
        "*Pontos fracos*",
        (", ".join(weaknesses) if weaknesses else "Nenhum ponto crítico forte"),
        "",
        "*Filtro pessoal sugerido*",
        "1) mantenha o que melhora sua ética e sua vida prática",
        "2) descarte o que opera por medo, culpa e submissão",
        "3) preserve autonomia intelectual",
        "4) compare discurso e prática",
    ])

    return "\n".join(lines)


def validate_twilio_request(req):
    if not VALIDATE_TWILIO:
        return True
    signature = req.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(req.url, req.form, signature)


def next_question_text(session: dict):
    idx = session.get("question_index", 0)
    _, question = QUESTIONS[idx]
    return question


def next_manipulation_text(session: dict):
    idx = session.get("manipulation_index", 0)
    _, question = MANIPULATION_CHECKS[idx]
    return question


@app.route("/health", methods=["GET"])
def health():
    return {"ok": True, "app": APP_TITLE}


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    if not validate_twilio_request(request):
        return Response("invalid signature", status=403)

    phone = (request.form.get("From") or "").strip()
    body = (request.form.get("Body") or "").strip()
    text = body.lower()

    session = get_session(phone)
    resp = MessagingResponse()
    msg = resp.message()

    if text in {"menu", "ajuda", "help"}:
        msg.body(MENU)
        return str(resp)

    if text == "reset":
        reset_session(phone)
        msg.body("Sessão reiniciada. Envie *iniciar* para começar de novo.")
        return str(resp)

    if text == "resumo":
        if session.get("state") != "done":
            msg.body("Ainda não há diagnóstico final. Envie *iniciar* para começar.")
        else:
            msg.body(build_summary(session))
        return str(resp)

    if text == "iniciar":
        reset_session(phone)
        update_session(phone, state="awaiting_religion")
        msg.body("Informe o nome da religião, tradição ou grupo que você quer analisar.")
        return str(resp)

    state = session.get("state", "idle")

    if state == "idle":
        msg.body(MENU)
        return str(resp)

    if state == "awaiting_religion":
        update_session(phone, religion_name=body, state="scoring", question_index=0)
        msg.body(f"Analisando: *{body}*\n\n{QUESTIONS[0][1]}")
        return str(resp)

    if state == "scoring":
        score = parse_score(body)
        if score is None:
            msg.body("Resposta inválida. Envie um número inteiro de 0 a 10.")
            return str(resp)

        idx = session.get("question_index", 0)
        key, _ = QUESTIONS[idx]
        update_session(phone, **{key: score})

        idx += 1
        if idx < len(QUESTIONS):
            update_session(phone, question_index=idx)
            new_session = get_session(phone)
            msg.body(next_question_text(new_session))
            return str(resp)

        update_session(phone, state="manipulation", manipulation_index=0)
        new_session = get_session(phone)
        msg.body(
            "Agora vamos ao teste de manipulação. Responda somente *sim* ou *nao*.\n\n"
            + next_manipulation_text(new_session)
        )
        return str(resp)

    if state == "manipulation":
        yn = parse_yes_no(body)
        if yn is None:
            msg.body("Resposta inválida. Responda apenas com *sim* ou *nao*.")
            return str(resp)

        idx = session.get("manipulation_index", 0)
        key, _ = MANIPULATION_CHECKS[idx]
        update_session(phone, **{key: yn})

        idx += 1
        if idx < len(MANIPULATION_CHECKS):
            update_session(phone, manipulation_index=idx)
            new_session = get_session(phone)
            msg.body(next_manipulation_text(new_session))
            return str(resp)

        update_session(phone, state="done")
        final_session = get_session(phone)
        msg.body(build_summary(final_session))
        return str(resp)

    if state == "done":
        msg.body("Diagnóstico já concluído. Envie *resumo* para ver de novo ou *reset* para iniciar outra análise.")
        return str(resp)

    msg.body("Estado inesperado. Envie *reset* para reiniciar.")
    return str(resp)


if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
