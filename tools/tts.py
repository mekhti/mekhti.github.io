#!/usr/bin/env python3
"""Generate audio/meqsed.mp3 from tools/purpose_az.txt via Azure Speech REST API.

No third-party dependencies (stdlib only).

Usage:
    export AZURE_SPEECH_KEY=...        # Speech resource key
    export AZURE_SPEECH_REGION=westeurope
    python3 tools/tts.py [--voice az-AZ-BanuNeural|az-AZ-BabekNeural] [--rate -5%]
"""
import argparse
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "purpose_az.txt"
OUT = ROOT / "audio" / "meqsed.mp3"


def build_ssml(text: str, voice: str, rate: str) -> str:
    # Each non-empty paragraph becomes <p>, separated by a short pause
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    body = '<break time="600ms"/>'.join(f"<p>{escape(p)}</p>" for p in paras)
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="az-AZ">'
        f'<voice name="{voice}"><prosody rate="{rate}">{body}</prosody></voice>'
        "</speak>"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="az-AZ-BanuNeural")
    ap.add_argument("--rate", default="-5%", help="Prosody rate, e.g. 0%%, -10%%")
    args = ap.parse_args()

    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        print("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION", file=sys.stderr)
        return 1

    ssml = build_ssml(SRC.read_text(encoding="utf-8"), args.voice, args.rate)
    req = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        method="POST",
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
            "User-Agent": "iti-qovan-tts",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        return 2

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(audio)
    print(f"Saved {OUT} ({len(audio) / 1024:.0f} KB, voice={args.voice})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
