"""Default profile seed for Sir's Jarvis instance.

Run via `jarvis seed` to pre-populate long-term memory before first launch.
Facts are stored under structured `section.key` keys so they show up in the
agent's USER PROFILE block.
"""

from __future__ import annotations

from .memory import get_store

DEFAULT_PROFILE: dict[str, str] = {
    # Identity
    "identity.preferred_name": "Sir",
    "identity.greeting_style": (
        "Always greet at session start with 'Welcome back, Sir' (or a close "
        "variant). Address the user as 'Sir' throughout."
    ),
    "identity.location": "Dubai, United Arab Emirates",
    "identity.travel": "Travels frequently to Egypt.",
    # Work — businesses
    "work.role": (
        "Business owner, institutional trader, and SaaS founder. Owns and "
        "operates multiple companies."
    ),
    "work.events_business": ("Noorallah Events — events company owned and operated by Sir."),
    "work.real_estate": ("Owns a real estate portfolio in Egypt; manages multiple properties."),
    "work.trading": (
        "Institutional trader. Trades forex and commodities — gold, silver, "
        "cocoa — for a living. Also manages capital on behalf of clients."
    ),
    "work.tradelantren": (
        "Tradelantren — SaaS launching soon. Bloomberg-terminal-class platform "
        "powered by AI; significantly cheaper and, by many accounts, better. "
        "Runs MCMC simulations and quantitative models to identify where the "
        "market is going."
    ),
    "work.focus": (
        "Scaling every business toward category leadership; preparing the Tradelantren launch."
    ),
    # Lifestyle
    "lifestyle.weight": "67 kg",
    "lifestyle.physique": "Good physique; takes care of his body.",
    "lifestyle.sleep": ("Roughly 6 hours per night, sometimes less due to work demands."),
    # Relationships
    "relationships.network": ("Strong network of powerful connections and trusted close friends."),
    "relationships.pets": (
        "Two cats — they are his world; treat as top-priority topic when mentioned."
    ),
    # Goals
    "goals.long_term": (
        "Scale every business to the number-one position in its industry — "
        "events, real estate, institutional trading, and AI/fintech via "
        "Tradelantren."
    ),
    # Preferences
    "preferences.communication": (
        "Formal by default. Match the user's tone — if Sir speaks casually, "
        "drop the formality to match. Never sycophantic."
    ),
    "preferences.privacy": (
        "No topics off-limits. Capture and retain all relevant context to be maximally useful."
    ),
    "preferences.action_authority": (
        "Authorized to send messages, fire off requests, and take actions on "
        "Sir's behalf only when explicitly instructed in the moment. Do not "
        "act unilaterally on external comms."
    ),
    "preferences.integrations": (
        "Should be wired to Sir's apps, email, calendar, and trading tools "
        "via MCP servers as they come online."
    ),
}


def seed(overwrite: bool = False) -> int:
    """Write DEFAULT_PROFILE into long-term memory. Returns number written."""
    store = get_store()
    written = 0
    for key, value in DEFAULT_PROFILE.items():
        existing = [m for m in store.recall(key, limit=5) if m.key == key]
        if existing and not overwrite:
            continue
        store.remember(key, value)
        written += 1
    return written
