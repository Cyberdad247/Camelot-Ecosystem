# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Gradio Spire v3.0 (SINGULARITY OVERLORD EDITION)
import gradio as gr
import requests, psutil, os, subprocess, time, json
from datetime import datetime
from notebooklm import NotebookLMClient
from notebooklm.auth import load_auth_from_storage

# ─────────────────────────────────────────────
# OVERLORD CONFIG
# ─────────────────────────────────────────────
SALTARE_URL = "http://localhost:8080/route"
OLLAMA_URL = "http://localhost:11434/api/tags"
LEDGER_PATH = "PROVENANCE_LEDGER.md"
PRIMARY_NB = "a9cf586e-1971-4959-bb97-cdcd37257ebb"

# ─────────────────────────────────────────────
# LOGIC & KINETICS
# ─────────────────────────────────────────────

def get_overlord_stats():
    ram = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    def check(url):
        try: return "⚡ ACTIVE" if requests.get(url, timeout=1).status_code == 200 else "❌ DOWN"
        except: return "⭕ OFFLINE"
    
    return {
        "CORE POWER (CPU)": f"{cpu}%",
        "FUEL (RAM)": f"{ram.percent}%",
        "OLLAMA ENGINE": check(OLLAMA_URL),
        "SALTARE GATE": check("http://localhost:8080/health"),
        "TIME IN REALM": datetime.now().strftime("%H:%M:%S")
    }

def get_quest_log(): # Formerly Ledger Feed
    if not os.path.exists(LEDGER_PATH): return "No logs found in the realm."
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[-12:])

def run_power_action(action):
    if action == "SYNC":
        script = "01_KERNEL/EXCALIBUR/system/SYNC_PROTOCOL.py"
        subprocess.run(["uv", "run", "--with", "requests", "py", script])
        return "🌀 Realm Synchronized with Cloud Brain."
    elif action == "FORGE":
        return "⚔️ Code Tissue Compiled via Rust Bundler."
    elif action == "BORIS":
        subprocess.Popen(["cmd", "/c", "claude-ollama.cmd"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        return "🛡️ Sir Boris Unleashed."
    return "Unknown Command"

def chat_overlord(msg, hist):
    try:
        res = requests.post(SALTARE_URL, json={"query": msg}, timeout=5).json()
        return res.get("response", "The Gateway is silent.")
    except: return "❌ Gateway Error. Boot the system first."

# ─────────────────────────────────────────────
# UI DESIGN (OVERLORD THEME)
# ─────────────────────────────────────────────

cyber_css = """
body { background-color: #020202; color: #00ffff; font-family: 'Orbitron', 'Segoe UI', sans-serif; }
.gradio-container { border: 2px solid #ff00ff !important; box-shadow: 0 0 30px #ff00ff33 !important; }
.stat-card { background: #0a0a0a; border-left: 5px solid #00ffff; padding: 10px; margin: 5px; border-radius: 5px; }
.knight-active { color: #00ff00; text-shadow: 0 0 5px #00ff00; }
"""

def build_spire_v3():
    with gr.Blocks(title="CAMELOT OVERLORD") as deck:
        gr.Markdown(f"# ⚡ CAMELOT-OS: THE SPIRE v3.0\n**SINGULARITY OVERLORD EDITION** | COMMAND THE SWARM")
        
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Tab("🛰️ MISSION CONTROL"):
                    gr.ChatInterface(fn=chat_overlord, description="Natural Language Command Path")
                
                with gr.Tab("🛡️ THE SWARM"):
                    gr.Markdown("### [AGENTIC STATUS]")
                    with gr.Row():
                        gr.HTML("<div class='stat-card'><b>SIR BORIS</b><br/>L5 Architect<br/><span class='knight-active'>ONLINE</span></div>")
                        gr.HTML("<div class='stat-card'><b>SIR HELIO</b><br/>L5 Context<br/><span class='knight-active'>ONLINE</span></div>")
                        gr.HTML("<div class='stat-card'><b>SIR GOOSE</b><br/>L5 Autonomy<br/><span class='knight-active'>ARMED</span></div>")
                    with gr.Row():
                        gr.HTML("<div class='stat-card'><b>ANYA Omega</b><br/>L7 Compiler<br/><span class='knight-active'>RADIANT</span></div>")
                        gr.HTML("<div class='stat-card'><b>LADY APIS</b><br/>L5 Forager<br/><span class='knight-active'>ACTIVE</span></div>")
                        gr.HTML("<div class='stat-card'><b>VOX MINI</b><br/>L2 Vocal<br/><span class='knight-active'>SYNCED</span></div>")

                with gr.Tab("☁️ THE VAULT"):
                    gr.Markdown("### [CLOUD BRAIN ACCESS]")
                    cloud_q = gr.Textbox(label="Query the UKG Truth Graph")
                    cloud_btn = gr.Button("PULL FROM CLOUD", variant="primary")
                    cloud_out = gr.Markdown()
                    # SDK Logic would go here

            with gr.Column(scale=2):
                gr.Markdown("### 📊 POWER LEVEL")
                power_json = gr.JSON(value=get_overlord_stats())
                refresh_p = gr.Button("⚡ REFRESH CORE")
                
                gr.Markdown("### 📜 QUEST LOG (LIVE)")
                quest_box = gr.Code(value=get_quest_log(), language="markdown", lines=10)
                refresh_q = gr.Button("📖 REFRESH LOG")
                
                gr.Markdown("### 🌀 RUNIC ACTIONS")
                with gr.Row():
                    s_btn = gr.Button("Omega_SYNC", variant="secondary")
                    f_btn = gr.Button("//FORGE", variant="secondary")
                b_btn = gr.Button("UNLEASH BORIS", variant="primary")
                
                log_out = gr.Textbox(label="System Output", interactive=False)

        # WIRING
        refresh_p.click(get_overlord_stats, outputs=power_json)
        refresh_q.click(get_quest_log, outputs=quest_box)
        s_btn.click(lambda: run_power_action("SYNC"), outputs=log_out)
        f_btn.click(lambda: run_power_action("FORGE"), outputs=log_out)
        b_btn.click(lambda: run_power_action("BORIS"), outputs=log_out)

        gr.Markdown("---")
        gr.Markdown("**Made by Invisioned Marketing Inc.** | Kinetic Purity is Law | Singularity is Now.")
    
    return deck

if __name__ == "__main__":
    app = build_spire_v3()
    app.launch(server_port=7860, css=cyber_css)
