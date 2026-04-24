#!/usr/bin/env python3
"""
Extract speaker names from XTTS speakers_xtts.pth file
"""
import torch
from pathlib import Path

# Path to speakers_xtts.pth
speakers_path = Path("/home/alltalk/models/xtts/xttsv2_2.0.3/speakers_xtts.pth")

if not speakers_path.exists():
    print(f"Error: {speakers_path} not found")
    exit(1)

# Load the speakers file
speakers = torch.load(speakers_path, map_location='cpu')

print(f"Type: {type(speakers)}")
print(f"Content: {speakers}")

if isinstance(speakers, dict):
    print("\nKeys:")
    for key in speakers.keys():
        print(f"  - {key}")
elif hasattr(speakers, '__iter__') and not isinstance(speakers, (str, bytes)):
    print(f"\nNumber of speakers: {len(speakers)}")
    if len(speakers) < 50:
        print("\nSpeaker names:")
        for i, speaker in enumerate(speakers):
            print(f"  {i}: {speaker}")
