"""
Agente 3 - The Copywriter

Toma los "dolores" detectados por el Agente 2 y redacta un Cold Email
Ofreciendo servicios, conectando específicamete con lo que hace la empresa.
Luego decide si enviar el email usando la tool send_email.

Misión: "La Conexión" - Unir punto A (Cliente) y punto B (Tu servicio).
"""

import os
import re
import sys
from typing import TypedDict

import yaml

# El agente vive en agents/Agent 3/, así que subimos dos niveles hasta Backend/.
SALIDAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Salidas de los Agentes")
_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt", "prompt_instruction.yaml")

#Agregar el directorio Backend al path para importar tools (dos niveles arriba)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from tools.send_email import send_email


def _load_prompt() -> str:
    """Carga el prompt desde prompt/prompt_instruction.yaml (ralativo a este archivo)."""
    with open(_PROMPT_PATH, encoding="utf-8") as f:
        return (yaml.safe_load(f) or {})["system_prompt"]
    

# -- Tipos para el grafo ---
class CopywriterState(TypedDict, total = False):
    """Estado: profile_data del Agente 2 + config de tu servicio."""
    profile_data: str
    my_service_info: str
    company_tone: str
    final_email: str
    recipient_email: str
    email_sent_status: str


# --- LLM con tools bindeados ---
# init_chat_model se mantiene porque create_agent NO acepta temperature como 
# parámetro; la temperatura se fija al inicializar el modelo y se pasa la instancia.
llm = init_chat_model("openai:gpt-4o", temperature=0.7)
tools = [send_email]

SYSTEM_PROMPT = _load_prompt()

copywriter_agent = create_agent(model= llm, tools=tools, system_prompt=SYSTEM_PROMPT)


def _extract_pain_points(profile_data: str) -> str:
    """Extrae la sección 'Puntos de Dolor' del perfil del Agente 2."""
    if not profile_data:
        return "(No se detectaron puntos de dolor)"
    pattern = r"\*\*Puntos de Dolor[^*]*\*\*[:\s]*(.*?)(?=\n\n\d\.|\n\n\*\*|\n\n##\Z)"
    match = re.search(pattern, profile_data, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return profile_data[:1500] if len(profile_data) > 1500 else profile_data


def copywriter_node(state: CopywriterState) -> dict[str, str]:
    """
    Nodo que genera el Cold Email y lo envía usando la tool send_email.
    EL agente ReAct decide cuándo invocar la tool.
    """
    profile_data = state.get("profile_data", "")
    my_service_info = state.get("my_service_info", "Soluciones de IA para empresas")
    company_tone = state.get("company_tone", "profesional y cercano")
    recipient_email = state.get("recipient_email", "")

    pain_points = _extract_pain_points(profile_data)

    # Firma real del remitente (desde .env), para que el LLM no invente placeholders
    firma = "\n".join(
        filter(
            None,
            [
                os.getenv("SENDER_NAME"),
                os.getenv("SENDER_POSITION"),
                os.getenv("SENDER_COMPANY"),
                os.getenv("SENDER_PHONE"),
                os.getenv("SENDER_EMAIL"),
            ],
        )
    )

    # Construir el mensaje para el agente
    user_message = f"""Genera un cold email con esta información:

Negocio del prospecto: {profile_data}
PUntos de dolor: {pain_points}
Nosotros vendemos: {my_service_info}
Tono deseado: {company_tone}

Firma el email exactamente con estos datos (no uses placeholders como [Tu Nombre]):
{firma}

Primero redacta el email completo.
"""
    if recipient_email:
        user_message += f"""
Luego envíalo usando la herramienta send_email con estos datos:
- recipient_email: {recipient_email}
- subject: Propuesta de colaboración - Soluciones de IA
- body: el email que acabas de redactar
"""
    
    print("[Agente 3] Copywriter (ReAct) generando email...", flush=True)

    result = copywriter_agent.invoke(
        {"messages": [HumanMessage(content=user_message)]}
    )

    #Extraer el email generado y el estado de envío de los mesajes
    messages = result["messages"]
    final_email = ""
    email_sent_status = ""

    for msg in messages:
        # El primer AIMessage con content es el email generado
        if msg.type == "ai" and msg.content and not final_email:
            final_email = msg.content
        # Los ToolMessages contienen el resultado del envío
        if msg.type == "tool" and msg.name == "send_email":
            email_sent_status = msg.content

    print("[Agente 3] Copywriter completado", flush=True)
    if email_sent_status:
        print(f"[Agente 3] {email_sent_status}", flush=True)

    # Guardas salida en documento para revisión
    run_id = state.get("run_id")
    if run_id:
        run_dir = os.path.join(SALIDAS_DIR, run_id)
        os.makedirs(run_dir, exist_ok=True)
        out_path = os.path.join(run_dir, "agente3_email.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_email)
        print(f"[Agente 3] Guardado: {out_path}", flush=True)

    return {"final_email": final_email, "email_sent_status": email_sent_status}