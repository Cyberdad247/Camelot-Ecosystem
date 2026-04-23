"""Camelot Knights - The Round Table.

All knight classes registered here for control plane dispatch.
"""

from .base import BaseKnight
from .boris import SirBoris
from .coder import SirForge
from .architect import SirSystema
from .debug import SirDebug
from .sentinel import SirSentinel
from .syntax import SirSyntax
from .forgemaster import SirForgeMaster
from .stitch import SirStitch
from .alchemist import SirAlchemist
from .vaelen import BaronVaelen
from .synthesis import SirSynthesis
from .lancelot import SirLancelot
from .agenteer import Agenteer
from .mnemo import SirMnemo
from .link import SirLink
from .sir_gideon import SirGideon
from .browser_nano_knight import (
    BrowserNanoKnight, NanoApis, NanoSentinel, NanoSyntax, NanoDebug, BrowserSquad,
)
from .researcher import *  # noqa: F401,F403
from .creative import *  # noqa: F401,F403
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
    "BrowserNanoKnight",
    "NanoApis",
    "NanoSentinel",
    "NanoSyntax",
    "NanoDebug",
    "BrowserSquad",
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
    # Browser Nano-Knights
    "nano_apis":      NanoApis,
    "nano_sentinel":  NanoSentinel,
    "nano_syntax":    NanoSyntax,
    "nano_debug":     NanoDebug,
}
