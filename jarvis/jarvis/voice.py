"""Voice mode for Jarvis using the OpenAI Realtime API.

The audio plumbing is adapted from the SDK's realtime CLI demo; it captures
mic input via sounddevice and streams playback through a callback-based
output stream.
"""

from __future__ import annotations

import asyncio
import queue
import threading
from typing import Any

import numpy as np
import sounddevice as sd

from agents.realtime import RealtimeAgent, RealtimeRunner, RealtimeSession, RealtimeSessionEvent

from .agent import _instructions
from .config import settings
from .integrations import build_servers
from .tools import ALL_TOOLS

CHUNK_LENGTH_S = 0.05
SAMPLE_RATE = 24000
FORMAT = np.int16
CHANNELS = 1


def _build_realtime_agent(mcp_servers=None) -> RealtimeAgent:
    return RealtimeAgent(
        name="Jarvis",
        instructions=_instructions(),
        tools=ALL_TOOLS,
        mcp_servers=mcp_servers or [],
    )


class VoiceLoop:
    def __init__(self) -> None:
        self.session: RealtimeSession | None = None
        self.audio_stream: sd.InputStream | None = None
        self.audio_player: sd.OutputStream | None = None
        self.recording = False
        self.output_queue: queue.Queue[Any] = queue.Queue(maxsize=10)
        self.interrupt_event = threading.Event()
        self.current_chunk: np.ndarray | None = None
        self.chunk_position = 0

    def _output_cb(self, outdata, frames, time_info, status) -> None:
        if self.interrupt_event.is_set():
            while not self.output_queue.empty():
                try:
                    self.output_queue.get_nowait()
                except queue.Empty:
                    break
            self.current_chunk = None
            self.chunk_position = 0
            self.interrupt_event.clear()
            outdata.fill(0)
            return

        outdata.fill(0)
        filled = 0
        while filled < len(outdata):
            if self.current_chunk is None:
                try:
                    self.current_chunk = self.output_queue.get_nowait()
                    self.chunk_position = 0
                except queue.Empty:
                    break
            remaining_out = len(outdata) - filled
            remaining_chunk = len(self.current_chunk) - self.chunk_position
            n = min(remaining_out, remaining_chunk)
            if n > 0:
                outdata[filled : filled + n, 0] = self.current_chunk[
                    self.chunk_position : self.chunk_position + n
                ]
                filled += n
                self.chunk_position += n
                if self.chunk_position >= len(self.current_chunk):
                    self.current_chunk = None
                    self.chunk_position = 0

    async def _capture(self) -> None:
        assert self.audio_stream and self.session
        read_size = int(SAMPLE_RATE * CHUNK_LENGTH_S)
        try:
            while self.recording:
                if self.audio_stream.read_available < read_size:
                    await asyncio.sleep(0.01)
                    continue
                data, _ = self.audio_stream.read(read_size)
                await self.session.send_audio(data.tobytes())
                await asyncio.sleep(0)
        finally:
            if self.audio_stream and self.audio_stream.active:
                self.audio_stream.stop()
            if self.audio_stream:
                self.audio_stream.close()

    async def _on_event(self, event: RealtimeSessionEvent) -> None:
        if event.type == "audio":
            np_audio = np.frombuffer(event.audio.data, dtype=np.int16)
            try:
                self.output_queue.put_nowait(np_audio)
            except queue.Full:
                if self.output_queue.qsize() > 8:
                    try:
                        self.output_queue.get_nowait()
                        self.output_queue.put_nowait(np_audio)
                    except queue.Empty:
                        pass
        elif event.type == "audio_interrupted":
            self.interrupt_event.set()
        elif event.type == "tool_start":
            print(f"  · tool: {event.tool.name}")
        elif event.type == "error":
            print(f"  ! error: {event.error}")

    async def run(self) -> None:
        print("[jarvis] connecting...")
        chunk = int(SAMPLE_RATE * CHUNK_LENGTH_S)
        self.audio_player = sd.OutputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype=FORMAT,
            callback=self._output_cb,
            blocksize=chunk,
        )
        self.audio_player.start()
        connected_servers = []
        for s in build_servers():
            try:
                await s.connect()
                connected_servers.append(s)
            except Exception as e:
                print(f"  ! integration {getattr(s, 'name', '?')} skipped: {e}")
        try:
            runner = RealtimeRunner(_build_realtime_agent(mcp_servers=connected_servers))
            async with await runner.run() as session:
                self.session = session
                self.audio_stream = sd.InputStream(
                    channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=FORMAT
                )
                self.audio_stream.start()
                self.recording = True
                asyncio.create_task(self._capture())
                print(f"[jarvis] online — voice: {settings.voice}. speak freely.")
                async for event in session:
                    await self._on_event(event)
        finally:
            if self.audio_player and self.audio_player.active:
                self.audio_player.stop()
            if self.audio_player:
                self.audio_player.close()
            for s in connected_servers:
                try:
                    await s.cleanup()
                except Exception:
                    pass


def run() -> None:
    try:
        asyncio.run(VoiceLoop().run())
    except KeyboardInterrupt:
        print("\n[jarvis] offline.")
