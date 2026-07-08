"""
Agente 1 - Scraper y Data Engineer (nodo LangGraph).

Este archivo es EL AGENT: contiene la inteligencia (limpieza con LLM vía
init_chat_model), la orquestación y el nodo `data_engineer_node` para el grafo.

Lo único separado es la extracción cruda de Apify, en scraper.py (no usa LLM).

El nodo scrapea la URL del estado y, según `skip_cleaning`, entrega texto raw
(rápido) o texto limpiado por LLM, guardando la salida en disco para revisión.

Documentación LangChain v1: https://docs.langchain.com/oss/python/releases/langchain-v1
"""

import importlib.util
import json
import os
from typing import Any

import yaml
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

# El agente vive en agents/Agent 1/, así que subimos dos niveles hasta Backend/.
_DIR = os.path.dirname(os.path.abspath(__file__))
SALIDAS_DIR = os.path.join(_DIR, "..", "..", "Salidas de los Agentes")
_PROMPT_PATH = os.path.join(_DIR, "prompt", "prompt_instruction.yaml")

# --- Configuración ---
MAX_CHUNK_CHARS = 8000  # Límite aproximado para evitar exceder contexto del LLM


def _load_local(mod_name: str, filename: str):
    """Carga un módulo vecion por ruta (nombre único para evitar colisiones en sys.modules)."""
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(_DIR, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)    #type:ignore
    return mod


# La extracción cruda (Apify, sin LLM) vive aparte en scraper.py
_scraper = _load_local("agente1_scraper", "scraper.py")
scrape_website = _scraper.scrape_website


def _load_prompt() -> str:
    """Carga el prompt dede prompt/prompt_instruction.yaml (relativo a este archivo)."""
    with open(_PROMPT_PATH, encoding="utf-8") as f:
        return(yaml.safe_load(f) or {})["system_prompt"]
    

def _split_content_for_llm(content: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Divide contenido largo en chunks para no exceder el contexto del LLM."""
    if len(content) <= max_chars:
        return [content] if content.strip() else[]
    
    chunks: list[str] = []
    start = 0
    while start < len(content):
        end = start + max_chars
        if end < len(content):
            # Intentar cortar en un salto de línea
            last_newline = content.rfind("\n", start, end)
            if last_newline > start:
                end = last_newline + 1
        chunks.append(content[start:end].strip())
        start = end

    return [c for c in chunks if c]


def clean_scraped_data(
        scraped_items: list[dict[str, Any]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        openai_api_key: str | None = None,
        system_prompt: str | None = None,
) -> list[dict[str, Any]]:
    """
    Limpia los datos scrapeados usando una LLM de OpenAI vía LangChain v1.

    La LLM elimina ruido, normaliza formato y preserva el contenido sustancial.

    Args:
        scraped_items: Salida de scrape_website()
        model: Modelo de OpenAI (default: gpt-4o-mini)
        temperature: Temperatura para la generación (0.0 para resultados determinados)
        openai_api_key: API key de OpenAI (o OPENAI_API_KEY en env)
        system_prompt: Prompt de sistema personalizado para la limpieza

    Returns:
        Lista de diccionarios con url, cleaned_text, metadata (y markdown si existía)
    """
    if not scraped_items:
        return []
    
    api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Se requiere OPENAI_API_KEY. "
            "Configúralo en el entorno o pásalo como openai_api_key."
        )
    
    llm = init_chat_model(
        f"openai:{model}",
        temperature = temperature,
        api_key = api_key,
    )

    sys_prompt = system_prompt or _load_prompt()

    cleaned: list[dict[str, Any]] = []

    for i, item in enumerate(scraped_items):
        url = item.get("url","")
        # Preferir markdown si existe, es más estructurado
        content = item.get("markdown") or item.get("text", "")
        metadata = item.get("metadata", {})

        print(f"[Agente 1] Limpiando página {i + 1}/{len(scraped_items)}...", flush=True)
        if not content or not content.strip():
            cleaned.append({
                "url": url,
                "cleaned_text": "",
                "metadata": metadata,
                **({"markdown": item.get("markdown")} if "markdown" in item else {}),
            })
            continue
        
        chunks = _split_content_for_llm(content)
        cleaned_parts: list[str] = []

        for chunk in chunks:
            user_msg = f"Limpia el siguiente contenido extraído de {url}:\n\n{chunk}"
            response = llm.invoke([
                SystemMessage(content=sys_prompt),
                HumanMessage(content=user_msg),
            ])
            if hasattr(response, "content") and response.content:
                cleaned_parts.append(response.content.strip())

        cleaned_text = "\n\n".join(cleaned_parts) if cleaned_parts else ""

        out: dict[str, Any] = {
            "url": url,
            "cleaned_text": cleaned_text,
            "metadata": metadata,
        }
        if "markdown" in item:
            out["markdown"] = item["markdown"]
        cleaned.append(out)

    print(f"[Agente 1] Limpieza completada: {len(cleaned)} páginas", flush=True)
    return cleaned


def run_scraper_and_clean(
        url: str,
        max_crawl_pages: int = 10,
        max_crawl_depth: int = 3,
        model: str = "gpt-4o-mini",
        skip_cleaning: bool = False,
        **kwargs: Any,
) -> list[dict[str, Any]]:
    """
    Pipeline completo: scrapea una website y opcionalmente limpia los datos con LLM.

    Args:
        url: URL de la website a scrapear
        max_crawl_pages: Máximo de páginas a rastrear
        model: Model OpenAI para la limpieza
        skip_cleaning: Si True, salta la limpieza con LLM (más rápido, usa texto raw)
        **kwargs: Argumentos adicionales para scrape_website y clean_scraped_data

    Returns:
        Lista de diccionarios con url, cleaned_text, metadata
    """
    scraped = scrape_website(url=url, max_crawl_pages=max_crawl_pages, max_crawl_depth=max_crawl_depth, **kwargs)
    if skip_cleaning:
        print("[Agente 1] Modo rápido: omitiendo limpieza LLM, pasando a Profiler...", flush=True)
        # Pasar texto raw al Profiler (mucho más rápido, evita timeout)
        return [
            {
                "url": item.get("url", ""),
                "cleaned_text": item.get("markdown") or item.get("text", ""),
                "metadata": item.get("metadata", {}),
            }
            for item in scraped
        ]
    return clean_scraped_data(scraped_items=scraped, model=model, **kwargs)


def data_engineer_node(state: dict) -> dict:
    """
    Nodo para LangGraph: scrapea y limpia la URL del estado.
    Espera state con 'target_url'; opcional: max_crawl_pages, my_service_info, company_tone.
    Devuelve {'cleaned_data': list[dict]}.
    """
    url = state.get("target_url", "")
    if not url:
         return {"cleaned_data": []}
    max_pages = state.get("max_crawl_pages", 10)
    max_depth = state.get("max_crawl_depth", 3)
    skip_cleaning = state.get("skip_cleaning", True) # True por defecto para evitar timeout
    results = run_scraper_and_clean(url=url, max_crawl_pages=max_pages, max_crawl_depth=max_depth, skip_cleaning=skip_cleaning)

    # Guarda salida en documento para revisión
    run_id = state.get("run_id")
    if run_id:
        run_dir = os.path.join(SALIDAS_DIR, run_id)
        os.makedirs(run_dir, exist_ok=True)
        out_path = os.path.join(run_dir, "agente1_datos_limpios.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"[Agente 1] Guardado: {out_path}", flush=True)

    return {"cleaned_data": results}


# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Requiere: APIFY_API_TOKEN y OPENAI_API_KEY en el entorno
    url_ejemplo = "https://docs.apify.com/"
    print("Scrapeando y limpiando ...")
    resultados = run_scraper_and_clean(url_ejemplo, max_crawl_pages=3)
    for r in resultados:
        print(f"\n--- {r['url']} ---")
        print(r["cleaned_text"][:500] + "..." if len(r["cleaned_text"])>500 else r["cleaned_text"])

