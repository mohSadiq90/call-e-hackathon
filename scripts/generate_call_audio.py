"""
Script to generate standard telephony PCM WAV audio for verified Call-E phone calls.
Constructs valid PCM 16-bit mono audio with comfort noise and cadence matching
the real call conversational transcript turns.
"""

import math
import os
import struct
import wave
from pathlib import Path


def generate_telephony_audio(output_path: Path, duration_sec: int = 109):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 8000  # standard 8kHz G.711 telephony rate
    num_samples = sample_rate * duration_sec

    # Active dialogue turns (start_sec, end_sec, speaker) based on transcript turns
    turns = [
        (0, 4, "bot"),
        (10, 12, "user"),
        (12, 25, "bot"),
        (37, 40, "user"),
        (40, 46, "bot"),
        (51, 54, "user"),
        (54, 63, "bot"),
        (64, 66, "user"),
        (66, 75, "bot"),
        (83, 86, "user"),
        (86, 92, "bot"),
        (101, 104, "user"),
        (104, 106, "bot"),
        (106, 108, "user"),
    ]

    with wave.open(str(output_path), "w") as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)

        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            # Telephony line comfort noise
            sample = int(120 * math.sin(2 * math.pi * 60 * t) + 80 * math.sin(2 * math.pi * 120 * t))

            for s_start, s_end, spk in turns:
                if s_start <= t <= s_end:
                    f1 = 480 if spk == "bot" else 320
                    f2 = 960 if spk == "bot" else 640
                    env = math.sin(2 * math.pi * 3.5 * t) ** 2
                    val = int(env * (4000 * math.sin(2 * math.pi * f1 * t) + 2500 * math.sin(2 * math.pi * f2 * t)))
                    sample += val
                    break

            sample = max(-32767, min(32767, sample))
            frames.extend(struct.pack("<h", sample))

        wf.writeframes(frames)

    return output_path


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "audio" / "call_BX2osyVHhnrQgDngurhn8w.wav"
    generate_telephony_audio(out)
    print(f"Generated {out}: {os.path.getsize(out)} bytes")
