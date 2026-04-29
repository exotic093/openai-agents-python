"""Web tools: HTTP fetch and lightweight search via DuckDuckGo."""

from __future__ import annotations

import re
from html.parser import HTMLParser

import httpx
from agents import function_tool

UA = "Mozilla/5.0 (compatible; Jarvis/0.1; +https://github.com/openai/openai-agents-python)"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        text = data.strip()
        if text:
            self._chunks.append(text)

    @property
    def text(self) -> str:
        return re.sub(r"\s+\n", "\n", "\n".join(self._chunks)).strip()


@function_tool
def fetch_url(url: str, max_chars: int = 4000) -> str:
    """Fetch a URL and return readable text content (HTML stripped)."""
    try:
        r = httpx.get(url, headers={"User-Agent": UA}, timeout=15, follow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        return f"Fetch failed: {e}"
    ctype = r.headers.get("content-type", "")
    if "html" in ctype:
        parser = _TextExtractor()
        parser.feed(r.text)
        body = parser.text
    else:
        body = r.text
    return body[:max_chars]


@function_tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web via DuckDuckGo's HTML endpoint and return top results."""
    try:
        r = httpx.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": UA},
            timeout=15,
        )
        r.raise_for_status()
    except Exception as e:
        return f"Search failed: {e}"
    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    results: list[str] = []
    for href, title, snippet in pattern.findall(r.text)[:max_results]:
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        clean_snippet = re.sub(r"<[^>]+>", "", snippet).strip()
        results.append(f"- {clean_title}\n  {href}\n  {clean_snippet}")
    return "\n\n".join(results) or "(no results)"
