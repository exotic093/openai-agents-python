"""Cross-platform desktop notifications and a tiny TTS hook."""

from __future__ import annotations

import platform
import shlex
import subprocess

from agents import function_tool


@function_tool
def notify(title: str, message: str, urgency: str = "normal") -> str:
    """Send a desktop notification to the user.

    Args:
        title: Short heading (e.g. "Jarvis").
        message: Body text.
        urgency: "low" | "normal" | "critical" (mapped where supported).
    """
    system = platform.system()
    try:
        if system == "Darwin":
            script = f"display notification {shlex.quote(message)} with title {shlex.quote(title)}"
            subprocess.Popen(["osascript", "-e", script])
        elif system == "Windows":
            ps = (
                "[Windows.UI.Notifications.ToastNotificationManager,"
                "Windows.UI.Notifications,ContentType=WindowsRuntime] | Out-Null;"
                f"$tpl = [Windows.UI.Notifications.ToastNotificationManager]::"
                "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]"
                "::ToastText02);"
                f"$tpl.GetElementsByTagName('text').Item(0).AppendChild("
                f"$tpl.CreateTextNode({shlex.quote(title)})) | Out-Null;"
                f"$tpl.GetElementsByTagName('text').Item(1).AppendChild("
                f"$tpl.CreateTextNode({shlex.quote(message)})) | Out-Null;"
                "[Windows.UI.Notifications.ToastNotificationManager]::"
                "CreateToastNotifier('Jarvis').Show("
                "[Windows.UI.Notifications.ToastNotification]::new($tpl))"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
        else:
            subprocess.Popen(
                [
                    "notify-send",
                    f"--urgency={urgency}",
                    title,
                    message,
                ]
            )
        return f"notified: {title} — {message}"
    except FileNotFoundError:
        return "no notification backend on this system."
    except Exception as e:
        return f"notify failed: {e}"


@function_tool
def speak(text: str) -> str:
    """Speak a short message aloud through the system's TTS."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["say", text])
        elif system == "Windows":
            ps = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak({shlex.quote(text)})"
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
        else:
            subprocess.Popen(["espeak", text])
        return "spoken."
    except FileNotFoundError:
        return "no TTS backend on this system."
    except Exception as e:
        return f"speak failed: {e}"
