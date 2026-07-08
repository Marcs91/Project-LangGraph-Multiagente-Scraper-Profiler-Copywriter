"""
Agente 2 - The Profiler

Analiza el modelo de negocio a partir de los datos scrapeados y limpios del Agente 1.
Enfocado en: Puntos de Dolor, tecnología usada, carencias y cliente ideal.

Recibe: cleaned_data (salida del Agente 1)
Devuelve: profile_data (perfil de negocio para el Agente 3)
"""

import os
from typing import Any, TypedDict

import yaml

# El agente vive en agents/Agent 2/, así que subimos dos niveles hasta Backend/.
SALIDAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Salidas de los Agentes")
_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt", "prompt_instruction.yaml")

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model


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


# --- Cadeena LCEL (definida fuera del nodo) ---
llm = init_chat_model("openai:gpt-4o", temperature=0.0)

prompt_profiler = ChatPromptTemplate.from_template(_load_prompt())

profiler_chain = prompt_profiler | llm | StrOutputParser()


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
    Nodo que analiza el modelo de negocio usando la cadena LCEL.
    Recibe cleaned_data del Agente 1 y devuelve profile_data.
    """
    cleaned_data = state.get("cleaned_data", [])
    website_content = _format_cleaned_data_for_prompt(cleaned_data)

    print("[Agente 2] Profiler ejecutando análisis...", flush=True)
    profile_result = profiler_chain.invoke({
        "website_content": website_content,
    })
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