"""Model provider selection with automatic fallback.

Picks a working model based on which API keys are present in the environment.
Order of preference (overridable via JARVIS_PROVIDER):

1. openai   — GPT-5 via native SDK, needs OPENAI_API_KEY.
2. claude   — Anthropic Claude via LiteLLM, needs ANTHROPIC_API_KEY.
3. gemini   — Google Gemini via LiteLLM, needs GEMINI_API_KEY.

If the preferred provider has no key, the selector falls through to the next
provider that does. If nothing is configured, we return the OpenAI default
and let the SDK error clearly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderChoice:
    """The selection result: which provider won, what model string to use."""

    name: str  # "openai" | "claude" | "gemini"
    model: str  # SDK-facing model identifier
    api_key_env: str  # env var that holds the key (for logging)

    @property
    def uses_litellm(self) -> bool:
        return self.name != "openai"


# Defaults — override any of these with JARVIS_<PROVIDER>_MODEL in .env.
DEFAULTS = {
    "openai": os.environ.get("JARVIS_OPENAI_MODEL", "gpt-5"),
    "claude": os.environ.get("JARVIS_CLAUDE_MODEL", "anthropic/claude-opus-4-7"),
    "gemini": os.environ.get("JARVIS_GEMINI_MODEL", "gemini/gemini-2.5-pro"),
}

_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def _has_key(provider: str) -> bool:
    return bool(os.environ.get(_KEY_ENV[provider]))


def _order() -> list[str]:
    """Return the preferred provider order, honoring JARVIS_PROVIDER."""
    preferred = (os.environ.get("JARVIS_PROVIDER") or "").strip().lower()
    fallback_chain = ["openai", "claude", "gemini"]
    if preferred in fallback_chain:
        # Preferred provider first, then the rest in default order.
        return [preferred] + [p for p in fallback_chain if p != preferred]
    return fallback_chain


def select() -> ProviderChoice:
    """Return the first provider whose API key is present."""
    for name in _order():
        if _has_key(name):
            return ProviderChoice(
                name=name,
                model=DEFAULTS[name],
                api_key_env=_KEY_ENV[name],
            )
    # Nothing configured — fall through to openai default so error messages
    # clearly point at OPENAI_API_KEY.
    return ProviderChoice(
        name="openai",
        model=DEFAULTS["openai"],
        api_key_env=_KEY_ENV["openai"],
    )


def build_model(choice: ProviderChoice):
    """Return an SDK-compatible model argument for `Agent(model=...)`.

    For OpenAI, returns the plain model string (native SDK handling).
    For Claude/Gemini, returns a LitellmModel instance.
    """
    if not choice.uses_litellm:
        return choice.model
    try:
        from agents.extensions.models.litellm_model import LitellmModel
    except ImportError as e:
        raise RuntimeError(
            f"Selected provider '{choice.name}' needs the litellm extra. "
            f"Install it: uv pip install 'openai-agents[litellm]' litellm."
        ) from e

    return LitellmModel(
        model=choice.model,
        api_key=os.environ.get(choice.api_key_env),
    )


def status_report() -> str:
    """Human-readable summary of which providers are configured."""
    active = select()
    lines = [f"active provider: [bold]{active.name}[/] · model {active.model}"]
    for name in ["openai", "claude", "gemini"]:
        marker = "●" if _has_key(name) else "○"
        lines.append(f"  {marker} {name:<7} ({_KEY_ENV[name]}) → {DEFAULTS[name]}")
    return "\n".join(lines)
