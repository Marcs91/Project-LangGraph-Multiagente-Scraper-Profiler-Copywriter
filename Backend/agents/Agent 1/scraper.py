"""
Agente 1 . Scraper - Extracción de contenido web

Responsabilidad única: scrapear una website con el Website Content Crawler de
Apify (apify/website-content-crawler) y devolver el contenido crudo.

La limpieza/normalización vive en clearner.py; la orquestación y el nodo del
grafo, en 'Agente 1 - Scraper y Data Engineer.py'.

Website Content Crawler: https://apify.com/apify/website-content-crawler
"""

import os
from typing import Any

from apify_client import ApifyClient


# --- Configuración ---
APIFY_ACTOR_ID = "apify/website-content-crawler"


def scrape_website(
        url: str,
        max_crawl_pages: int = 1,
        max_crawl_depth: int | None = None,
        use_markdown: bool = True,
        apify_token: str | None = None,
) -> list[dict[str, Any]]:
    """
    Extrae contenido de una website usando el Website Content Crawler de Apify.

    Args:
        url: URL de inicio para el crawl (ej: "https://docs.apify.com/")
        max_crawl_pages: Número máximo de páginas a rastrear (default: 10)
        max_crawl_depth: Profundidad máxima del crawl (opcional)
        use_markdown: Si True, incluye el campo markdown; si False, solo text
        apify_token: Token de Apify (o APIFY_API_TOKEN en env)

    Returns:
        Lista de diccionarios con: url, text, markdown (opcional), metadata

    Raises:
        ValueError: Si no hay APIFY_API_TOKEN configurado
    """
    token = apify_token or os.environ.get("APIFY_API_TOKEN")
    if not token:
        raise ValueError(
            "Se requiere APIFY_API_TOKEN. "
            "Configúralo en el entorno o pásalo como apify_token."
        )
    
    client = ApifyClient(token)

    run_input: dict[str, Any] = {
        "startUrls": [{"url": url}],
        "maxCrawlPages": max_crawl_pages,
    }
    if max_crawl_depth is not None:
        run_input["maxCrawlDepth"] = max_crawl_depth

    print("[Agente 1] Iniciando scrape con Apify...", flush=True)
    run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)
    dataset_id = run["defaultDatasetId"] if isinstance(run, dict) else run.default_dataset_id
    dataset = client.dataset(dataset_id)

    results: list[dict[str, Any]] = []
    for item in dataset.iterate_items():
        entry: dict[str, Any] = {
            "url": item.get("url", ""),
            "text": item.get("text") or "",
            "metadata": item.get("metadata", {}),
        }
        if use_markdown and item.get("markdown"):
            entry["markdown"] = item["markdown"]
        results.append(entry)

    print(f"[Agente 1] Scrape completado: {len(results)} páginas", flush=True)
    return results
