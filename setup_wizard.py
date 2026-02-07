#!/usr/bin/env python3
"""
Telegram MCP Setup Wizard

Generates session string and outputs ready-to-use config for both
Claude Desktop and Claude Code.

Usage:
    # Interactive (asks for everything):
    docker run -it --rm bayramannakov/telegram-mcp:latest python setup_wizard.py

    # Pre-fill API credentials (skips credential prompts):
    docker run -it --rm bayramannakov/telegram-mcp:latest python setup_wizard.py \
        --api-id 12345678 --api-hash abc123def456

    # Demo mode (no real connection):
    docker run -it --rm bayramannakov/telegram-mcp:latest python setup_wizard.py --demo
"""

import sys
import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Telegram MCP Setup Wizard")
    parser.add_argument("--api-id", type=int, help="Telegram API ID (from my.telegram.org)")
    parser.add_argument("--api-hash", type=str, help="Telegram API Hash (from my.telegram.org)")
    parser.add_argument("--demo", "-d", action="store_true", help="Demo mode — show example output")
    return parser.parse_args()


def print_config(api_id, api_hash, session_string):
    """Print both Claude Desktop and Claude Code configurations."""
    # Claude Desktop config
    config = {
        "mcpServers": {
            "telegram": {
                "command": "docker",
                "args": [
                    "run", "--rm", "-i",
                    "-e", f"TELEGRAM_API_ID={api_id}",
                    "-e", f"TELEGRAM_API_HASH={api_hash}",
                    "-e", f"TELEGRAM_SESSION_STRING={session_string}",
                    "bayramannakov/telegram-mcp:latest"
                ]
            }
        }
    }

    print()
    print("=" * 58)
    print("  Option A: Claude Desktop")
    print("=" * 58)
    print()
    print("Paste this into your claude_desktop_config.json:")
    print()
    print("-" * 58)
    print(json.dumps(config, indent=2))
    print("-" * 58)
    print()
    print("Config file location:")
    print("  Mac:     ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print()

    # Claude Code command
    print("=" * 58)
    print("  Option B: Claude Code (CLI)")
    print("=" * 58)
    print()
    print("Run this command in your terminal:")
    print()
    print("-" * 58)
    # Build the claude mcp add command
    docker_cmd = (
        f"claude mcp add telegram-mcp -s user -- "
        f"docker run --rm -i "
        f"-e TELEGRAM_API_ID={api_id} "
        f"-e TELEGRAM_API_HASH={api_hash} "
        f"-e TELEGRAM_SESSION_STRING={session_string} "
        f"bayramannakov/telegram-mcp:latest"
    )
    print(docker_cmd)
    print("-" * 58)
    print()
    print("Then restart Claude Code and test:")
    print('  "Show my unread Telegram messages"')
    print()


def show_demo():
    """Demo mode — shows example output without real credentials."""
    print()
    print("=" * 58)
    print("  Telegram MCP Setup Wizard (DEMO MODE)")
    print("=" * 58)
    print()
    print("Step 1: Enter your Telegram API credentials")
    print("        (from https://my.telegram.org)")
    print()
    print("API ID (number): 12345678")
    print("API Hash (string): abc123def456ghi789jkl012")
    print()
    print("-" * 58)
    print("Step 2: Connect your Telegram account")
    print("-" * 58)
    print()
    print("Phone number: +1234567890")
    print("Enter code: 12345")
    print()
    print("=" * 58)
    print("  SUCCESS! Here's your config.")
    print("=" * 58)

    print_config("YOUR_API_ID", "YOUR_API_HASH", "YOUR_SESSION_STRING")


def main():
    args = parse_args()

    if args.demo:
        show_demo()
        return

    from telethon.sync import TelegramClient
    from telethon.sessions import StringSession

    print()
    print("=" * 58)
    print("  Telegram MCP Setup Wizard")
    print("=" * 58)
    print()

    # Step 1: Get API credentials (from args or interactive)
    if args.api_id and args.api_hash:
        api_id = args.api_id
        api_hash = args.api_hash
        print(f"Using provided credentials (API ID: {api_id})")
        print()
    else:
        print("Step 1: Enter your Telegram API credentials")
        print("        (from https://my.telegram.org)")
        print()

        api_id_str = input("API ID (number): ").strip()
        api_hash = input("API Hash (string): ").strip()

        if not api_id_str or not api_hash:
            print("\nError: Both API ID and API Hash are required.")
            sys.exit(1)

        try:
            api_id = int(api_id_str)
        except ValueError:
            print("\nError: API ID must be a number.")
            sys.exit(1)

    print("-" * 58)
    print("Step 2: Connect your Telegram account")
    print("-" * 58)
    print()
    print("A verification code will be sent to your Telegram app.")
    print()

    try:
        with TelegramClient(StringSession(), api_id, api_hash) as client:
            session_string = StringSession.save(client.session)

            print()
            print("=" * 58)
            print("  SUCCESS! Here's your config.")
            print("=" * 58)

            print_config(api_id, api_hash, session_string)

    except Exception as e:
        print(f"\nError: {e}")
        print("Please check your credentials and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
