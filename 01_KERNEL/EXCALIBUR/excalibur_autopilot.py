# [SYSTEM] :: EXCALIBUR_AUTOPILOT_v87.0
# [ARCHITECT] :: SIR SYSTÉMA & SIR KINETIC
# [CONTEXT] :: Invisioned Marketing inc. (S-Corp) // Camelot-OS
# [MANDATE] :: Automate the SIT-Loop (Sense -> Think -> Persist)
# "Made by Invisioned Marketing inc."

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# --- PHASE I: INFRASTRUCTURE ---
import google.generativeai as genai
import replicate
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [G.E.M.] - %(levelname)s - %(message)s')
logger = logging.getLogger("EXCALIBUR")

class ExcaliburEngine:
    def __init__(self):
        self._bootstrap_environment()
        self._init_appwrite()
        self._init_gemini()
        self._init_replicate()
        
    def _bootstrap_environment(self):
        """Load environment variables and validate existence."""
        load_dotenv()
        self.APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
        self.APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
        self.APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
        self.APPWRITE_DB_ID = os.getenv("APPWRITE_DB_ID")
        self.APPWRITE_COL_ID = os.getenv("APPWRITE_COLLECTION_ID")
        
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

        missing = []
        if not self.APPWRITE_API_KEY: missing.append("APPWRITE_API_KEY")
        if not self.GOOGLE_API_KEY: missing.append("GOOGLE_API_KEY")
        
        if missing:
            logger.critical(f"MISSING KEYS: {missing}. HALTING.")
            sys.exit(1)

    def _init_appwrite(self):
        """Connect to the Appwrite Fortress."""
        try:
            self.client = Client()
            self.client.set_endpoint(self.APPWRITE_ENDPOINT)
            self.client.set_project(self.APPWRITE_PROJECT_ID)
            self.client.set_key(self.APPWRITE_API_KEY)
            self.db = Databases(self.client)
            logger.info("⚔️ Appwrite Connection: ESTABLISHED")
        except Exception as e:
            logger.critical(f"Appwrite Handshake Failed: {e}")
            sys.exit(1)

    def _init_gemini(self):
        """Awaken the Brain."""
        try:
            genai.configure(api_key=self.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-3-pro-preview')
            self.chat_session = self.model.start_chat(history=[])
            logger.info("🧠 Gemini 3 Pro: ONLINE")
        except Exception as e:
            logger.critical(f"Gemini Handshake Failed: {e}")
            sys.exit(1)

    def _init_replicate(self):
        """Prepare the Forge (GPU)."""
        # Replicate SDK checks env var REPLICATE_API_TOKEN automatically
        if not self.REPLICATE_API_TOKEN:
            logger.warning("⚠️ REPLICATE_API_TOKEN not found. Image generation disabled.")
        else:
            logger.info("🎨 Replicate GPU: STANDBY")

    # --- PHASE IV: ERROR RECOVERY (OCTOPUS LOGIC) ---
    def _retry_operation(self, operation, name="Operation", retries=1):
        """
        [OCTOPUS] Logic: Attempt recursive retry before failure.
        """
        try:
            return operation()
        except Exception as e:
            if retries > 0:
                logger.warning(f"⚠️ {name} failed. Retrying... ({retries} left)")
                time.sleep(2)
                return self._retry_operation(operation, name, retries - 1)
            else:
                logger.error(f"❌ {name} CRITICAL FAILURE: {e}")
                return None

    # --- PHASE II: THE SIT-LOOP ---
    
    def sense(self) -> str:
        """
        SENSE: Fetch the last state/context from Appwrite.
        """
        def _fetch():
            try:
                result = self.db.list_documents(
                    database_id=self.APPWRITE_DB_ID,
                    collection_id=self.APPWRITE_COL_ID,
                    queries=[Query.order_desc('$createdAt'), Query.limit(1)]
                )
                if result['documents']:
                    return result['documents'][0].get('content', 'No previous state.')
                return "No previous state."
            except Exception as e:
                # If DB doesn't exist yet, return neutral state
                logger.warning(f"Sense check failed (DB might be empty): {e}")
                return "Initial State."

        return self._retry_operation(_fetch, "Sense_State")

    def think(self, user_input: str, context: str) -> str:
        """
        THINK: Process input via Gemini with Ω_TRINITY validation.
        """
        prompt = f"""
        [SYSTEM]: You are G.E.M. (Global Engineering Mentor) for Camelot-OS.
        [CONTEXT]: Last State: {context}
        [USER]: {user_input}
        
        [PRIME_DIRECTIVE]:
        1. Analyze if this moves the "Invisioned Marketing inc. Agentic Pivot" forward.
        2. If 'Ω_actuate' is invoked, describe the visual to be generated.
        3. Be concise, sovereign, and code-forward.
        
        [RESPONSE]:
        """
        
        def _generate():
            response = self.chat_session.send_message(prompt)
            return response.text

        return self._retry_operation(_generate, "Gemini_Reasoning")

    def persist(self, role: str, content: str):
        """
        PERSIST: Save state to the StateLog.
        """
        def _save():
            data = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': 'Excalibur_v87'
            }
            # Note: Ensure your Appwrite collection has these attributes or is permissive
            self.db.create_document(
                self.APPWRITE_DB_ID,
                self.APPWRITE_COL_ID,
                ID.unique(),
                data
            )
            
        self._retry_operation(_save, "Persist_Log")

    def actuate_visual(self, prompt: str):
        """
        ACTUATE: Trigger Replicate for image generation.
        """
        logger.info(f"🎨 Generating Visual Artifact: {prompt[:50]}...")
        
        def _paint():
            # Using a standard fast model - Flux or similar
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": prompt}
            )
            # Output is usually a list of URLs/Streams
            url = output[0] if isinstance(output, list) else output
            logger.info(f"✅ Visual Generated: {url}")
            return str(url)

        return self._retry_operation(_paint, "Replicate_Forge")

    # --- PHASE III: G.E.M. INTERFACE ---
    
    def engage(self):
        print("\n" + "="*60)
        print("⚔️ EXCALIBUR AUTOPILOT v87.0 :: ONLINE")
        print("   Type 'exit' to quit. Type 'Ω_actuate [prompt]' to forge visuals.")
        print("="*60 + "\n")

        while True:
            try:
                user_input = input("\n[👤] COMMAND > ")
                if user_input.lower() in ['exit', 'quit']:
                    print("[G.E.M.] Powering down. Systems secure.")
                    break

                # 1. SENSE
                last_state = self.sense()

                # 2. ACTUATE CHECK
                if user_input.startswith("Ω_actuate"):
                    visual_prompt = user_input.replace("Ω_actuate", "").strip()
                    if not visual_prompt:
                        visual_prompt = "Cybernetic Camelot control deck, sci-fi interface, high tech"
                    
                    img_url = self.actuate_visual(visual_prompt)
                    response_text = f"Visual Artifact Forged: {img_url}"
                    print(f"\n[🎨] REPLICATE > {img_url}")
                    
                    # Persist the artifact link
                    self.persist("replicate", response_text)
                    continue

                # 3. THINK
                response = self.think(user_input, last_state)
                
                # 4. PERSIST (User input and AI response)
                self.persist("user", user_input)
                self.persist("gemini", response)

                # Output
                print(f"\n[💎] G.E.M. > {response}")

            except KeyboardInterrupt:
                print("\n[G.E.M.] Manual Override. Shutting down.")
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")

if __name__ == "__main__":
    engine = ExcaliburEngine()
    engine.engage()
