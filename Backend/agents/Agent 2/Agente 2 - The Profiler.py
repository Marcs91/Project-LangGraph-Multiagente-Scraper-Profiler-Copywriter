"""
Agente 2 - The Profiler

Analiza el modelo de negocio a partir de los datos scrapeados y limpios del Agente 1.
Enfocado en: Puntos de Dolor, tecnología usada, carencias y cliente ideal.
Puede complementar el análisis con búsquedas en internet vía la tool tavily_search.

Recibe: cleaned_data (salida del Agente 1)
Devuelve: profile_data (perfil de negocio para el Agente 3)
"""

import os
from typing import Any, TypedDict

import yaml

# El agente vive en agents/Agent 2/, así que subimos dos niveles hasta Backend/.
SALIDAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Salidas de los Agentes")
_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt", "prompt_instruction.yaml")

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch


def _load_prompt() -> str:
    """Carga el prompt desde prompt/prompt_instruction.yaml (relativo a este archivo)."""
    with open(_PROMPT_PATH, encoding="utf-8") as f:
        return (yaml.safe_load(f) or {})["system_prompt"]


# --- Tipos para el grafo ---
class ProfilerState(TypedDict, total=False):
    """Estado esperado: cleaned_data viene del Agente 1."""
    cleaned_data: list[dict[str, Any]]
    profile_data: str
    url: str


# --- Agente ReAct con tool de búsqueda web (definido fuera del nodo) ---
llm = init_chat_model("openai:gpt-4o", temperature=0.0)
tools = [TavilySearch(max_results=5)]

SYSTEM_PROMPT = _load_prompt()

profiler_agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)


def _format_cleaned_data_for_prompt(cleaned_data: list[dict[str, Any]]) -> str:
    """Conviert la salida del Agente 1 en texto para el prompt."""
    parts: list[str] = []
    for item in cleaned_data:
        url = item.get("url", "(sin URL)")
        text = item.get("cleaned_text", "")
        if text:
            parts.append(f"### Página: {url}\n{text}")
    return "\n\n---\n\n".join(parts) if parts else "(No hay contenido disponible)"


def profiler_node(state: ProfilerState) -> dict[str, str]:
    """
    Nodo que analiza el modelo de negocio usando el agente ReAct.
    Recibe cleaned_data del Agente 1 y devuelve profile_data.
    El agente puede usar tavily_search si el contenido scrapeado no alcanza.
    """
    cleaned_data = state.get("cleaned_data", [])
    website_content = _format_cleaned_data_for_prompt(cleaned_data)

    user_message = f"""Analiza el siguiente contenido extraído de la website del prospecto y genera el Perfil de Negocio:

<contenido_website>
{website_content}
</contenido_website>

Si el contenido no es suficiente para cubrir alguna sección, usa la herramienta tavily_search
para investigar en internet (ej: noticias recientes, reputación, competidores). Luego entrega
el Perfil de Negocio completo.
"""

    print("[Agente 2] Profiler ejecutando análisis...", flush=True)
    result = profiler_agent.invoke(
        {"messages": [HumanMessage(content=user_message)]}
    )

    # La respuesta final es el último AIMessage con contenido (posterior a cualquier tool call)
    messages = result["messages"]
    profile_result = ""
    for msg in messages:
        if msg.type == "ai" and msg.content:
            profile_result = msg.content
    print("[Agente 2] Profiler completado", flush=True)

    # Guardar salida en documento para revisión
    run_id = state.get("run_id")
    if run_id:
        run_dir = os.path.join(SALIDAS_DIR, run_id)
        os.makedirs(run_dir, exist_ok=True)
        out_path = os.path.join(run_dir, "agente2_perfil.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(profile_result)
        print(f"[Agente 2] Guardado: {out_path}", flush=True)

    return {"profile_data": profile_result}
