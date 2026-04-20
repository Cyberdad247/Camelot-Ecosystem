# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys
from typing import TypedDict

import requests
from langgraph.graph import END, StateGraph

# Add KERNEL to path for telemetry import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
try:
    from senses.telemetry_client import RotelClient
    telemetry = RotelClient("local_intelligence")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): pass
    telemetry = DummyLogger()


class AgentState(TypedDict):
    prompt: str
    response: str
    model_path: str
    status: str


# KOBOLDCPP CONFIG
KOBOLD_API_URL = "http://localhost:5001/api/v1/generate"


def inference_node(state: AgentState) -> AgentState:
    """🛠️ INFERENCE_NODE (Sir Llama): Local LLM inference via koboldcpp."""
    telemetry.info("LOCAL_INFERENCE_START", prompt=state['prompt'][:50])
    print(f"[LLAMA] Processing prompt: {state['prompt'][:50]}...")

    payload = {
        "prompt": state["prompt"],
        "max_context_length": 2048,
        "max_length": 512,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    try:
        # This assumes koboldcpp is running on port 5001
        response = requests.post(KOBOLD_API_URL, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            state["response"] = result["results"][0]["text"]
            state["status"] = "SUCCESS"
            telemetry.info("LOCAL_INFERENCE_COMPLETE", status="SUCCESS")
        else:
            state["status"] = f"ERROR: KoboldCPP returned {response.status_code}"
            telemetry.error("LOCAL_INFERENCE_FAILED", code=response.status_code)
    except Exception as e:
        state["status"] = f"ERROR: Could not connect to KoboldCPP (Check if it's running). {e}"
        state["response"] = "Local inference failed. Please ensure koboldcpp is active."
        telemetry.error("LOCAL_INFERENCE_EXCEPTION", error=str(e))

    return state


# BUILD THE INTELLIGENCE SWARM
builder = StateGraph(AgentState)
builder.add_node("inference", inference_node)
builder.set_entry_point("inference")
builder.add_edge("inference", END)

local_intel_swarm = builder.compile()


def ask_local_ai(prompt: str):
    """Bridge to the local intelligence swarm."""
    initial_state = {
        "prompt": prompt,
        "response": "",
        "model_path": r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\koboldcpp\models\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "status": "INIT",
    }
    return local_intel_swarm.invoke(initial_state)


if __name__ == "__main__":
    # Test Run (Requires koboldcpp to be running)
    print("--- LOCAL INTELLIGENCE SWARM TEST ---")
    res = ask_local_ai("What is the meaning of Camelot?")
    print(f"Status: {res['status']}")
    print(f"Response: {res['response']}")