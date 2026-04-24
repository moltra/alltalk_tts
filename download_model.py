#!/usr/bin/env python3
"""
Model Download CLI Script for AllTalk TTS

This script provides a command-line interface for downloading TTS models.
It can be used standalone or within a Docker container.

Usage:
    python download_model.py --model xtts
    python download_model.py --model piper --list
    docker exec alltalk-dev python download_model.py --model xtts
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from system.config.firstrun import download_tts_model, unzip_compressed_files, update_tts_engines

this_dir = Path(__file__).parent.resolve()


def list_available_models(engine: str):
    """List available models for a given TTS engine."""
    available_models_path = this_dir / "system" / "tts_engines" / engine / "available_models.json"
    
    if not available_models_path.exists():
        print(f"❌ No available_models.json found for engine: {engine}")
        print(f"   Models for this engine may need to be downloaded manually.")
        return
    
    try:
        with open(available_models_path) as f:
            data = json.load(f)
            print(f"\n📦 Available models for {engine}:")
            print(f"   Default first-start model: {data.get('first_start_model', 'N/A')}")
            print(f"\n   Models:")
            for model in data.get("models", []):
                print(f"   • {model.get('model_name', 'Unknown')}")
                if "description" in model:
                    print(f"     {model['description']}")
    except Exception as e:
        print(f"❌ Error reading available models: {e}")


def check_model_exists(engine: str, model_name: str = None):
    """Check if a model is already downloaded."""
    models_dir = this_dir / "models" / engine
    
    if not models_dir.exists():
        return False
    
    # Check if directory has any model files
    model_files = list(models_dir.rglob("*.pth")) + list(models_dir.rglob("*.onnx")) + list(models_dir.rglob("*.json"))
    
    if model_files:
        print(f"✅ Found existing model files in {models_dir}")
        for f in model_files[:5]:  # Show first 5 files
            print(f"   • {f.name}")
        if len(model_files) > 5:
            print(f"   ... and {len(model_files) - 5} more files")
        return True
    
    return False


def download_model(engine: str, force: bool = False):
    """Download a TTS model."""
    print(f"\n🚀 Starting download for {engine} model...")
    
    # Check if model already exists
    if not force and check_model_exists(engine):
        response = input(f"\n⚠️  Model files already exist. Download anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Download cancelled.")
            return False
    
    # Attempt download
    success = download_tts_model(engine, on_download_completed=unzip_compressed_files)
    
    if success:
        print(f"\n✅ Successfully downloaded {engine} model!")
        print(f"   Model location: {this_dir / 'models' / engine}")
        
        # Ask if user wants to set this as the active engine
        response = input(f"\n🔧 Set {engine} as the active TTS engine? (Y/n): ")
        if response.lower() != 'n':
            update_tts_engines(engine)
            print(f"✅ {engine} is now the active TTS engine")
    else:
        print(f"\n❌ Failed to download {engine} model")
        print(f"   You may need to download it manually or check available_models.json")
        print(f"\n💡 Manual download instructions:")
        if engine == "xtts":
            print(f"   XTTS models can be downloaded from:")
            print(f"   https://huggingface.co/coqui/XTTS-v2")
        elif engine == "piper":
            print(f"   Piper models can be downloaded from:")
            print(f"   https://huggingface.co/rhasspy/piper-voices")
        elif engine == "vits":
            print(f"   VITS models can be downloaded from:")
            print(f"   https://github.com/jaywalnut310/vits")
        elif engine == "f5tts":
            print(f"   F5-TTS models can be downloaded from:")
            print(f"   https://huggingface.co/SWivid/F5-TTS")
        elif engine == "parler":
            print(f"   Parler models can be downloaded from:")
            print(f"   https://huggingface.co/Parler-TTS")
    
    return success


def main():
    parser = argparse.ArgumentParser(
        description="AllTalk TTS Model Download CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download XTTS model
  python download_model.py --model xtts
  
  # List available models for Piper
  python download_model.py --model piper --list
  
  # Force re-download even if model exists
  python download_model.py --model vits --force
  
  # Use from Docker
  docker exec alltalk-dev python download_model.py --model xtts
        """
    )
    
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        choices=["xtts", "piper", "vits", "f5tts", "parler"],
        required=True,
        help="TTS engine/model to download"
    )
    
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available models for the specified engine"
    )
    
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force download even if model already exists"
    )
    
    parser.add_argument(
        "--check",
        "-c",
        action="store_true",
        help="Check if model is already downloaded"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎙️  AllTalk TTS Model Download CLI")
    print("=" * 60)
    
    if args.list:
        list_available_models(args.model)
        return
    
    if args.check:
        exists = check_model_exists(args.model)
        if exists:
            print(f"✅ Model {args.model} is already downloaded")
        else:
            print(f"❌ Model {args.model} is not downloaded")
        return
    
    # Download the model
    success = download_model(args.model, force=args.force)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Download completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Download failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
