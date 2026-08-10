"""Camelot Knights - The Round Table.

All knight classes registered here for control plane dispatch.
"""

from .agenteer import Agenteer
from .alchemist import SirAlchemist
from .architect import SirSystema
from .base import BaseKnight
from .boris import SirBoris
from .browser_nano_knight import (
    BrowserNanoKnight,
    BrowserSquad,
    NanoApis,
    NanoDebug,
    NanoSentinel,
    NanoSyntax,
)
from .browser_research_agency import BrowserResearchAgency, BrowserScout
from .coder import SirForge
from .creative import *  # noqa: F401,F403
from .debug import SirDebug
from .forgemaster import SirForgeMaster
from .lancelot import SirLancelot
from .link import SirLink
from .mnemo import SirMnemo
from .researcher import *  # noqa: F401,F403
from .sentinel import SirSentinel
from .sir_gideon import SirGideon
from .sir_helio import SirHelio
from .stitch import SirStitch
from .syntax import SirSyntax
from .synthesis import SirSynthesis
from .vaelen import BaronVaelen
from .warden import *  # noqa: F401,F403

__all__ = [
    "BaseKnight",
    "SirBoris",
    "SirForge",
    "SirSystema",
    "SirDebug",
    "SirSentinel",
    "SirSyntax",
    "SirForgeMaster",
    "SirStitch",
    "SirAlchemist",
    "BaronVaelen",
    "SirSynthesis",
    "SirLancelot",
    "Agenteer",
    "SirMnemo",
    "SirLink",
    "SirGideon",
    "SirHelio",
    "BrowserNanoKnight",
    "NanoApis",
    "NanoSentinel",
    "NanoSyntax",
    "NanoDebug",
    "BrowserSquad",
    "BrowserResearchAgency",
    "BrowserScout",
]

# Knight registry for dynamic dispatch by name
KNIGHT_REGISTRY: dict[str, type[BaseKnight]] = {
    "sir_boris":      SirBoris,
    "sir_forge":      SirForge,
    "sir_systema":    SirSystema,
    "sir_debug":      SirDebug,
    "sir_sentinel":   SirSentinel,
    "sir_syntax":     SirSyntax,
    "sir_forgemaster": SirForgeMaster,
    "sir_stitch":     SirStitch,
    "sir_alchemist":  SirAlchemist,
    "baron_vaelen":   BaronVaelen,
    "sir_synthesis":  SirSynthesis,
    "sir_lancelot":   SirLancelot,
    "agenteer":       Agenteer,
    "sir_mnemo":      SirMnemo,
    "sir_link":       SirLink,
    "sir_gideon":     SirGideon,
    "gideon":         SirGideon,
    "sir_helio":      SirHelio,
    # Browser Nano-Knights
    "nano_apis":      NanoApis,
    "nano_sentinel":  NanoSentinel,
    "nano_syntax":    NanoSyntax,
    "nano_debug":     NanoDebug,
}

