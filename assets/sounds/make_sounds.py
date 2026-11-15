"""Generates the game's sound effects as small WAV files (our own work, no third-party audio).

Run it once from the repository root:  uv run python assets/sounds/make_sounds.py
It only uses the Python standard library.
"""

import math
import struct
import wave
from pathlib import Path

RATE = 22050  # samples per second
VOLUME = 0.35  # 0..1, kept low so the effects are not too loud
HERE = Path(__file__).resolve().parent


def tone(start_hz: float, end_hz: float, seconds: float) -> list[float]:
    """A sine wave that glides from start_hz to end_hz, with a short fade in and out (no clicks)."""
    n = int(RATE * seconds)
    samples, phase = [], 0.0
    for i in range(n):
        freq = start_hz + (end_hz - start_hz) * i / n
        phase += 2 * math.pi * freq / RATE
        fade = min(1.0, i / (0.005 * RATE), (n - i) / (0.01 * RATE))
        samples.append(math.sin(phase) * fade)
    return samples


def notes(*pairs: tuple[float, float]) -> list[float]:
    """A melody: (frequency in Hz, duration in seconds) one after the other."""
    result: list[float] = []
    for freq, seconds in pairs:
        result += tone(freq, freq, seconds)
    return result


def save(name: str, samples: list[float]) -> None:
    """Write mono 16-bit PCM."""
    with wave.open(str(HERE / f"{name}.wav"), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(b"".join(struct.pack("<h", int(s * VOLUME * 32767)) for s in samples))


if __name__ == "__main__":
    save("dot", tone(450, 900, 0.05))
    save("energizer", tone(300, 1200, 0.25))
    save("fruit", notes((660, 0.07), (880, 0.07), (1320, 0.12)))
    save("win", notes((523, 0.15), (659, 0.15), (784, 0.15), (1047, 0.35)))
    save("lose", tone(800, 100, 0.9))
    print("sounds written to", HERE)
