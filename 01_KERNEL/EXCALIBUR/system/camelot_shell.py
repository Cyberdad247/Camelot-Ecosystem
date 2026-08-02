# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys
import traceback

# PATH CONFIGURATION
sys.path.append(os.path.join(os.getcwd(), "01_ACTIVE_CORE"))
sys.path.append(os.getcwd())

from merlin_omega import Merlin_Omega
from src.camelot_cli.core.handlers import CommandHandlers
from src.camelot_cli.core.parser import CommandParser


# ==========================================
# 🦁 CAMELOT SHELL v1.0
# ==========================================
async def main_repl():
    print("\n" + "=" * 50)
    print("🦁 CAMELOT OS v100.0 [SHELL]")
    print("   Type '//HELP' for commands.")
    print("=" * 50 + "\n")

    # Initialize Kernel
    try:
        merlin = Merlin_Omega()
        print("✅ MERLIN_OMEGA LINKED.")
    except Exception as e:
        print(f"❌ KERNEL ERROR: {e}")
        traceback.print_exc()
        return

    while True:
        try:
            user_input = input("👑 SOVEREIGN> ")
            if not user_input.strip():
                continue

            # 1. Parse
            msg_type, cmd, args = CommandParser.parse(user_input)

            # 2. Route
            if msg_type == "SLASH":
                CommandHandlers.handle_slash(cmd, args)

            elif msg_type == "RUNE":
                CommandHandlers.handle_rune(cmd, args)

            else:
                # Natural Language -> Merlin
                print("🧠 [MERLIN] Thinking...")
                response = await merlin.process_request(user_input)
                print(f"💡 {response}")

        except KeyboardInterrupt:
            print("\n👋 Session Paused.")
            break
        except Exception as e:
            print(f"❌ SHELL ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main_repl())