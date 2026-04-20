# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os

REGISTRY_PATH = r"c:\Users\vizio\CAMELOT_OS\01_KERNEL\config\mcp_registry.json"


def verify_mcp_servers():
    if not os.path.exists(REGISTRY_PATH):
        print(f"❌ Registry not found at {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, "r") as f:
        config = json.load(f)

    tools = config.get("mcp_tools", [])
    print(f"[*] Found {len(tools)} MCP servers in registry.")

    for tool in tools:
        print(f"\n--- Verifying {tool['name']} ({tool['id']}) ---")
        cmd = tool["command"]
        print(f"Command: {' '.join(cmd)}")

        # We won't actually run them here as they might be long-running
        # but we can check if the paths exist locally for node/python ones
        if cmd[0] in ["node", "python", "npx"]:
            if len(cmd) > 1 and os.path.isabs(cmd[1] if cmd[0] == "node" else ""):  # Simple check for absolute paths
                target = cmd[1] if cmd[0] == "node" else ""
                if target and not os.path.exists(target):
                    print(f"[!] Warning: Target path {target} does not exist.")
                else:
                    print("[+] Path verified.")
            else:
                print(f"[+] Tool is command-based ({cmd[0]}).")


if __name__ == "__main__":
    verify_mcp_servers()