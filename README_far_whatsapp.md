# FAR Bot para WhatsApp

Bot de WhatsApp em Python + Flask + Twilio para aplicar o framework FAR (auditoria de religiões).

## O que ele faz

- recebe mensagens do WhatsApp via webhook
- conduz uma análise em etapas
- coleta notas de 0 a 10 para os 7 critérios do FAR
- aplica 4 checagens de manipulação
- devolve um diagnóstico final com total, classificação e filtro pessoal sugerido
- salva o estado da conversa em SQLite

## Arquivos

- `app_far_whatsapp.py`
- `requirements_far_whatsapp.txt`

## Requisitos

- Python 3.11+
- conta Twilio
- Sandbox do WhatsApp da Twilio ou número em produção
- ngrok ou outro túnel HTTPS para teste local

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements_far_whatsapp.txt
```

## Variáveis de ambiente

No Linux/macOS:

```bash
export PORT=5000
export DB_PATH=far_bot.db
export TWILIO_AUTH_TOKEN=seu_auth_token
export VALIDATE_TWILIO=true
```

No Windows PowerShell:

```powershell
$env:PORT="5000"
$env:DB_PATH="far_bot.db"
$env:TWILIO_AUTH_TOKEN="seu_auth_token"
$env:VALIDATE_TWILIO="true"
```

## Executar

```bash
python app_far_whatsapp.py
```

## Teste local com ngrok

```bash
ngrok http 5000
```

Pegue a URL HTTPS gerada e configure no painel da Twilio como webhook de entrada do WhatsApp:

```text
https://SEU-ENDERECO.ngrok-free.app/whatsapp
```

## Fluxo de uso

No WhatsApp, envie:

- `iniciar`
- informe o nome da religião
- responda as 7 notas
- responda as 4 perguntas de manipulação

Comandos extras:

- `menu`
- `ajuda`
- `reset`
- `resumo`

## Observações

- Se você estiver só testando localmente, pode deixar `VALIDATE_TWILIO=false`.
- Em produção, ative a validação da assinatura da Twilio.
- O bot atual é determinístico, sem LLM. Isso reduz custo e simplifica o controle do fluxo.

## Próxima evolução recomendada

- painel web para histórico de análises
- exportação em PDF
- múltiplos idiomas
- envio do resumo para e-mail
- integração com OpenAI para comentários mais sofisticados após o diagnóstico
