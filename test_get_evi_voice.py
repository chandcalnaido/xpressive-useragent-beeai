#!/usr/bin/env python3
"""
Test script to retrieve EVI configuration and extract voice details
"""
import asyncio
import os
from dotenv import load_dotenv
from hume.client import AsyncHumeClient

# Load environment variables
load_dotenv()

async def main():
    # Get credentials from environment
    api_key = os.getenv("HUME_API_KEY")
    config_id = os.getenv("HUME_CONFIG_ID")

    print("="*70)
    print("Retrieving EVI Configuration")
    print("="*70)
    print(f"Config ID: {config_id}")
    print()

    # Initialize Hume client
    client = AsyncHumeClient(api_key=api_key)

    try:
        # Get the EVI configuration (try version 0 and 1)
        for version in [0, 1]:
            try:
                print(f"Trying version {version}...")
                config = await client.empathic_voice.configs.get_config_version(
                    id=config_id,
                    version=version
                )

                print(f"\n✓ Successfully retrieved config version {version}")

                if hasattr(config, 'name'):
                    print(f"  Config Name: {config.name}")

                if hasattr(config, 'voice'):
                    print(f"\n  Voice Configuration Found:")
                    voice = config.voice

                    # Try to extract voice details
                    if hasattr(voice, 'id'):
                        print(f"    ✓ Voice ID: {voice.id}")
                    if hasattr(voice, 'name'):
                        print(f"    ✓ Voice Name: {voice.name}")
                    if hasattr(voice, 'provider'):
                        print(f"    ✓ Voice Provider: {voice.provider}")

                    # Show all attributes
                    print(f"\n  All voice attributes:")
                    if hasattr(voice, '__dict__'):
                        for key, value in voice.__dict__.items():
                            print(f"    {key}: {value}")
                    else:
                        print(f"    {voice}")

                    print("\n" + "="*70)
                    print("SUCCESS: Voice configuration retrieved!")
                    print("="*70)
                    break
                else:
                    print("  ❌ No voice configuration found")

            except Exception as e:
                print(f"  Version {version} failed: {e}")
                continue

    except Exception as e:
        print(f"\n❌ Error retrieving config: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
