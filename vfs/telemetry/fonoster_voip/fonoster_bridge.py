# SPDX-License-Identifier: MIT
"""Fonoster Telephony Bridge for Camelot Multivoice-Router.

Routes SIP/VoIP trunking, outbound calls, and webhook events into Hermes and Sonus.
"""

from __future__ import annotations

import json
from typing import Dict, Any


def build_fonoster_call_spec(to_number: str, webhook_url: str) -> Dict[str, Any]:
    return {
        "provider": "fonoster",
        "action": "outbound_call",
        "to": to_number,
        "webhook_url": webhook_url,
        "codec": "OPUS",
        "sample_rate": 48000,
        "max_duration_sec": 300,
    }


if __name__ == "__main__":
    print(json.dumps(build_fonoster_call_spec("+15550199", "https://camelot-os.dev/api/voip/webhook"), indent=2))
