from typing import Any

import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    if not settings.openrouter_api_key:
        return "OpenRouter API key is not configured. Please set OPENROUTER_API_KEY."

    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-OpenRouter-Title": settings.openrouter_app_name,
    }
    payload: dict[str, Any] = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful educational LLM consultant. Answer clearly and safely.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"OpenRouter network error: {exc}") from exc

    if response.status_code >= 400:
        raise RuntimeError(f"OpenRouter error {response.status_code}: {response.text[:300]}")

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenRouter response format: {data}") from exc

    if not content:
        return "OpenRouter returned an empty response."
    return str(content)
