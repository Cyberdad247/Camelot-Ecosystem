// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// AVATAR MANAGER (Mobile Logic)
// Maps Backend Personas to Frontend Assets & Voice Profiles

export type KnightPersona = "Merlin_Ω" | "Lukas_Ω" | "Anya_Ω" | "Sir_Sentinel";

export interface AvatarState {
  id: KnightPersona;
  asset: string; // Mock path to local asset
  voiceId: string;
  color: string;
  statusMsg: string;
}

const PROFILES: Record<KnightPersona, AvatarState> = {
  "Merlin_Ω": {
    id: "Merlin_Ω",
    asset: "🔮", // In real app: require('./assets/merlin.riv')
    voiceId: "onyx",
    color: "#8A2BE2", // Purple
    statusMsg: "Architecting Strategy..."
  },
  "Lukas_Ω": {
    id: "Lukas_Ω",
    asset: "🦫", // In real app: require('./assets/lukas.riv')
    voiceId: "echo",
    color: "#FF8C00", // Orange
    statusMsg: "Forging Artifacts..."
  },
  "Anya_Ω": {
    id: "Anya_Ω",
    asset: "🎭", // In real app: require('./assets/anya.riv')
    voiceId: "nova",
    color: "#00FFFF", // Cyan
    statusMsg: "Awaiting Input"
  },
  "Sir_Sentinel": {
    id: "Sir_Sentinel",
    asset: "🛡️", // In real app: require('./assets/sentinel.riv')
    voiceId: "fable",
    color: "#FF0000", // Red
    statusMsg: "Scanning Perimeter..."
  }
};

export class AvatarManager {
  static getState(persona: KnightPersona): AvatarState {
    return PROFILES[persona] || PROFILES["Anya_Ω"];
  }
}