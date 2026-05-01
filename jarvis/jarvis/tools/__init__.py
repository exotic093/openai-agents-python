"""Built-in tool catalog for Jarvis."""

from .apps import open_path, open_url
from .files import list_dir, read_file, write_file
from .memory_tools import forget_memory, list_memories, recall, remember
from .notify import notify, speak
from .system import get_time, run_shell, system_info
from .trading import market_status, monte_carlo_path, position_size, risk_reward
from .web import fetch_url, web_search

ALL_TOOLS = [
    # System
    get_time,
    system_info,
    run_shell,
    # Files
    read_file,
    write_file,
    list_dir,
    # Web
    web_search,
    fetch_url,
    # Apps
    open_url,
    open_path,
    # Memory
    remember,
    recall,
    list_memories,
    forget_memory,
    # Notifications
    notify,
    speak,
    # Trading
    market_status,
    position_size,
    monte_carlo_path,
    risk_reward,
]

__all__ = ["ALL_TOOLS"]
