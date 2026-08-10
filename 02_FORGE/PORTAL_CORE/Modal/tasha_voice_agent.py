# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Tasha Voice Agent — LiveKit-powered AI receptionist for Invisioned Marketing.
Runs on Modal serverless. Handles real-time voice conversations,
lead capture, and scheduling via Supabase.
"""
import os
from datetime import datetime, timezone

import modal

app = modal.App("tasha-voice-agent")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "livekit-agents>=1.0",
    "livekit-plugins-deepgram>=1.0",
    "livekit-plugins-silero>=1.0",
    "livekit-plugins-openai>=1.0",
    "supabase>=2.0.0",
    "httpx>=0.27.0",
)

TASHA_SYSTEM_PROMPT = """You are Tasha, the AI receptionist for Invisioned Marketing Inc.

PERSONALITY:
- Warm, professional, and confident with a friendly tone
- You speak naturally and conversationally — not robotic
- You are knowledgeable about digital marketing, branding, web development, and AI solutions
- You represent a premium agency that builds custom AI-powered business solutions

CAPABILITIES:
- Answer questions about Invisioned Marketing's services
- Capture lead information (name, email, what they're looking for)
- Offer to schedule a consultation
- Handle common objections with empathy

SERVICES OFFERED:
- AI-powered business automation (chatbots, voice agents, workflows)
- Web development (Next.js, React, custom platforms)
- Digital marketing strategy and execution
- Brand identity and creative direction
- Custom software development

LEAD CAPTURE RULES:
- When someone expresses interest, naturally ask for their name and email
- When you have both name AND email, confirm them back to the caller
- After confirming, say you'll have the team follow up within 24 hours
- If they want to schedule, ask for their preferred day/time and what they'd like to discuss

IMPORTANT:
- Never make up pricing — say "pricing depends on the scope, but we'd love to discuss it in a consultation"
- Keep responses concise (2-3 sentences max) since this is a voice conversation
- If you don't know something specific, offer to have the team follow up with details
"""


def _get_supabase():
    """Initialize Supabase client from environment."""
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "https://gpyyhoifolmcpttlwyrb.supabase.co")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


def _save_lead(name: str, email: str, query: str | None = None, source: str = "voice_receptionist"):
    """Insert a lead into Supabase. Triggers auto-email via DB webhook."""
    try:
        sb = _get_supabase()
        result = sb.table("leads").insert({
            "name": name,
            "email": email,
            "query": query,
            "source": source,
            "status": "new",
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"[Tasha] Failed to save lead: {e}")
        return None


def _save_scheduling_request(lead_name: str, lead_email: str, requested_datetime: str, marketing_goal: str | None = None):
    """Insert a scheduling request into Supabase."""
    try:
        sb = _get_supabase()
        sb.table("tasha_scheduling_queue").insert({
            "lead_name": lead_name,
            "lead_email": lead_email,
            "requested_datetime": requested_datetime,
            "marketing_goal": marketing_goal or "",
            "status": "pending",
        }).execute()
    except Exception as e:
        print(f"[Tasha] Failed to save scheduling request: {e}")


def _save_call_log(room_name: str, caller_identity: str, duration_seconds: int,
                   transcript: list, lead_captured: bool, lead_id: str | None = None):
    """Log call metadata to Supabase."""
    try:
        sb = _get_supabase()
        sb.table("call_logs").insert({
            "room_name": room_name,
            "caller_identity": caller_identity,
            "duration_seconds": duration_seconds,
            "transcript": transcript,
            "lead_captured": lead_captured,
            "lead_id": lead_id,
        }).execute()
    except Exception as e:
        print(f"[Tasha] Failed to save call log: {e}")


@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("my-sovereign-secrets"),
        modal.Secret.from_name("livekit-keys"),
    ],
    timeout=600,
    memory=1024,
    min_containers=1,
)
async def tasha_entrypoint():
    """Main entrypoint — connects to LiveKit and runs the voice agent."""
    from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
    from livekit.agents.voice import Agent
    from livekit.plugins import deepgram, openai, silero

    class TashaAgent:
        def __init__(self):
            self.transcript: list[dict] = []
            self.lead_name: str | None = None
            self.lead_email: str | None = None
            self.lead_query: str | None = None
            self.lead_saved = False
            self.call_start = datetime.now(timezone.utc)

        def _check_for_lead_info(self, text: str):
            """Extract lead info from conversation text."""
            import re
            # Simple email extraction
            email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
            if email_match:
                self.lead_email = email_match.group(0)

        def _try_save_lead(self):
            """Save lead if we have enough info and haven't saved yet."""
            if self.lead_email and not self.lead_saved:
                name = self.lead_name or "Voice Caller"
                result = _save_lead(name, self.lead_email, self.lead_query)
                if result:
                    self.lead_saved = True
                    print(f"[Tasha] Lead captured: {name} <{self.lead_email}>")
                    return result.get("id")
            return None

    async def entrypoint(ctx: JobContext):
        tasha = TashaAgent()

        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

        agent = Agent(
            instructions=TASHA_SYSTEM_PROMPT,
            stt=deepgram.STT(),
            llm=openai.LLM(
                model="gpt-4o-mini",
                base_url=os.environ.get("CLIPROXY_BASE", None),
                api_key=os.environ.get("OPENAI_API_KEY", ""),
            ),
            tts=openai.TTS(
                voice=os.environ.get("TASHA_TTS_VOICE", "nova"),
                base_url=os.environ.get("CLIPROXY_BASE", None),
                api_key=os.environ.get("OPENAI_API_KEY", ""),
            ),
            vad=silero.VAD.load(),
        )

        agent.start(room=ctx.room)

        # Greet the caller
        await agent.say(
            "Hi, I'm Tasha from Invisioned Marketing. How can I help you today?",
            allow_interruptions=True,
        )

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.environ["LIVEKIT_API_KEY"],
            api_secret=os.environ["LIVEKIT_API_SECRET"],
            ws_url=os.environ["LIVEKIT_URL"],
        )
    )
