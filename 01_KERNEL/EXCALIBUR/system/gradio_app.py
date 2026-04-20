# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
CAMELOT GRADIO INTERFACE [ANYA_Ω]
Sovereign Neural Interface for Camelot-OS.
"""

import os
import requests
import gradio as gr
from datetime import datetime

# Made by Invisioned Marketing inc.

KERNEL_URL = os.getenv("KERNEL_URL", "http://localhost:8000")

def send_intent(message, history):
    """Route intent to Merlin Kernel."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        response = requests.post(f"{KERNEL_URL}/command", params={"intent": message}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            decision = data.get("decision", {})
            action = decision.get("action", "PROCESSED")
            target = decision.get("target", "UKG")
            return f"[{timestamp}] [MERLIN_Ω] :: Action: {action} | Target: {target}"
        else:
            return f"[{timestamp}] [ERROR] :: Kernel responded with status {response.status_code}"
    except Exception as e:
        return f"[{timestamp}] [ERROR] :: Failed to link with Kernel: {str(e)}"

# Custom CSS for Radiant UI
custom_css = """
footer {visibility: hidden}
.gradio-container {background-color: #0b0e14; color: #e0e0e0;}
"""

with gr.Blocks(title="Camelot-OS Spire") as demo:
    gr.Markdown("# 🏰 CAMELOT-OS: SOVEREIGN SPIRE")
    gr.Markdown("### [ANYA_Ω] :: Intent Compiler Interface")
    
    with gr.Tab("Neural Link"):
        chat = gr.ChatInterface(
            send_intent,
            description="Direct neural link to MERLIN_Ω core logic.",
            examples=["//SWARM", "//HEAL", "System status report", "Who is vega?"],
        )
    
    with gr.Tab("System Status"):
        with gr.Row():
            gr.Label("OS VERSION: v300.4.0")
            gr.Label("STATUS: RADIANT")
            gr.Label("LATTICE: STABLE")

if __name__ == "__main__":
    # Ignite interface
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft(),
        css=custom_css,
        quiet=True
    )
