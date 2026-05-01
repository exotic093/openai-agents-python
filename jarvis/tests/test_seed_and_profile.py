"""Tests for the profile seed + profile_block formatting."""

from __future__ import annotations

import importlib

from jarvis import memory, profile, seed_data


def test_seed_writes_all_facts() -> None:
    importlib.reload(memory)
    importlib.reload(seed_data)
    n = seed_data.seed()
    assert n == len(seed_data.DEFAULT_PROFILE)
    # Idempotent — second run writes nothing.
    assert seed_data.seed() == 0


def test_seed_overwrite_rewrites() -> None:
    importlib.reload(memory)
    importlib.reload(seed_data)
    seed_data.seed()
    n = seed_data.seed(overwrite=True)
    assert n == len(seed_data.DEFAULT_PROFILE)


def test_profile_block_groups_by_section() -> None:
    importlib.reload(memory)
    importlib.reload(seed_data)
    importlib.reload(profile)
    seed_data.seed()
    block = profile.profile_block()
    assert "[identity]" in block
    assert "[work]" in block
    assert "preferred_name" in block
    assert "Sir" in block


def test_is_onboarded_flips_after_seed() -> None:
    importlib.reload(memory)
    importlib.reload(seed_data)
    importlib.reload(profile)
    assert profile.is_onboarded() is False
    seed_data.seed()
    assert profile.is_onboarded() is True
