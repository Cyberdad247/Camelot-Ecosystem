# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# [SYSTEM] :: EXCALIBUR_AUTOPILOT_v89.0 [OLLAMA_KINETIC]
# [ARCHITECT] :: SIR SYSTÉMA & SIR KINETIC
# [CONTEXT] :: Invisioned Marketing inc. (S-Corp) // Camelot-OS
# [MANDATE] :: Automate the SIT-Loop (Sense -> Think -> Persist) via LOCAL COMPUTE.

import json
import logging
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

# Add KERNEL to path for telemetry import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from senses.telemetry_client import RotelClient
    telemetry = RotelClient("excalibur")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): pass
    telemetry = DummyLogger()

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [EXCALIBUR] - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger("EXCALIBUR")


class OllamaBrain:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        self.headers = {"Content-Type": "application/json"}
        self._verify_connection()

    def _verify_connection(self):
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    logger.info(f"🧠 Ollama Kinetic Mesh: ONLINE [{self.model}]")
                    return
        except Exception as e:
            logger.critical(f"⚠️ Ollama Unreachable at {self.base_url}: {e}")
            sys.exit(1)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Execute a generation cycle. Returns the raw text response.
        """
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n[USER]: {user_prompt}",
            "stream": False,
            "options": {"temperature": 0.7, "num_ctx": 4096},
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}/api/generate", data=data, headers=self.headers)

        start_time = time.time()
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))

                # Benchmarking
                duration = time.time() - start_time
                eval_speed = result.get("eval_count", 0) / (result.get("eval_duration", 1) / 1e9)
                logger.info(f"⚡ Think Time: {duration:.2f}s | Speed: {eval_speed:.2f} t/s")

                return result.get("response", "").strip()
        except urllib.error.HTTPError as e:
            logger.error(f"Ollama API Error: {e.code} - {e.reason}")
            return f"Error: {e.reason}"
        except Exception as e:
            logger.error(f"Kinetic Failure: {e}")
            return "Error: Kinetic Failure"


class ExcaliburEngine:
    def __init__(self):
        self._bootstrap_environment()
        self.brain = OllamaBrain(self.OLLAMA_URL, self.OLLAMA_MODEL)

    def _bootstrap_environment(self):
        load_dotenv()
        self.OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

    def log_kinetic(self, actor: str, action: str, status: str):
        """Log to PROVENANCE_LEDGER.md via the Rust Kinetic Binary."""
        try:
            subprocess.run(
                ["./ledger.exe", "log", "--actor", actor.lower(), "--action", action, "--status", status],
                check=True,
                capture_output=True,
            )
        except Exception as e:
            logger.error(f"Failed to write to Kinetic Ledger: {e}")

    def sense(self) -> str:
        """SENSE: Read the last 5 lines of the Ledger."""
        try:
            if os.path.exists("CAMELOT_OS/PROVENANCE_LEDGER.md"):
                with open("CAMELOT_OS/PROVENANCE_LEDGER.md", "r") as f:
                    lines = f.readlines()
                    return "".join(lines[-5:]).strip()
            return "No previous state."
        except Exception:
            return "Initial State."

    def think(self, user_input: str, context: str) -> str:
        """THINK: Process input via Ollama."""
        system_prompt = f"""
        You are EXCALIBUR, the Autonomous Kernel of Camelot-OS.
        
        [CONTEXT]: 
        {context}
        
        [DIRECTIVE]:
        1. Analyze the User's command + Ledger Context.
        2. Provide a Sovereign, Code-Forward response.
        3. Do not be chatty. Be an Operator.
        """
        return self.brain.generate(system_prompt, user_input)

    def engage(self):
        telemetry.info("EXCALIBUR_ENGAGED", model=self.OLLAMA_MODEL)
        print("\n" + "=" * 60)
        print(f"⚔️ EXCALIBUR v89.0 [OLLAMA::{self.OLLAMA_MODEL.upper()}] :: ONLINE")
        print("   Type 'exit' to quit. 'switch [model]' to change kinetic engine.")
        print("=" * 60 + "\n")

        self.log_kinetic("MERLIN", f"EXCALIBUR_v89_ONLINE_MODEL_{self.OLLAMA_MODEL}", "SUCCESS")

        while True:
            try:
                user_input = input("\n[👤] COMMAND > ")

                # Local Command Handling
                if user_input.lower() in ["exit", "quit"]:
                    telemetry.info("EXCALIBUR_DISENGAGING")
                    self.log_kinetic("MERLIN", "EXCALIBUR_SHUTDOWN", "SUCCESS")
                    print("[G.E.M.] Systems Disengaging.")
                    break

                if user_input.startswith("switch "):
                    new_model = user_input.split(" ")[1]
                    telemetry.info("EXCALIBUR_ENGINE_SWITCH", old_model=self.OLLAMA_MODEL, new_model=new_model)
                    self.brain.model = new_model
                    self.OLLAMA_MODEL = new_model
                    print(f"[⚙️] Switched Kinetic Engine to: {new_model}")
                    self.log_kinetic("MERLIN", f"ENGINE_SWITCH_{new_model.upper()}", "SUCCESS")
                    continue

                # 1. SENSE
                last_state = self.sense()

                # 2. THINK
                response = self.think(user_input, last_state)

                # 3. ACT (Log Interaction)
                self.log_kinetic("MERLIN", f"CMD: {user_input[:30]}...", "SUCCESS")

                # Output
                print(f"\n[💎] RESPONSE > {response}")

            except KeyboardInterrupt:
                print("\n[G.E.M.] Manual Override. Shutting down.")
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")


if __name__ == "__main__":
    engine = ExcaliburEngine()
    engine.engage()