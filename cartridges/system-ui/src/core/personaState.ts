interface PersonaConfig {
  name: string;
  emotion: string;
  voicePitch: number;
  voiceSpeed: number;
}

export class PersonaStateManager {
  private activePersona = 'Anya';
  private configs: Record<string, PersonaConfig> = {
    Anya: { name: 'Anya', emotion: 'CREATIVE_BRUTALIST', voicePitch: 1.2, voiceSpeed: 1.1 },
    Merlin: { name: 'Merlin', emotion: 'LOGIC_STRICT', voicePitch: 0.8, voiceSpeed: 0.95 },
    Boris: { name: 'Boris', emotion: 'RESOURCE_CONCENTRATE', voicePitch: 0.9, voiceSpeed: 1.0 },
  };

  public getActivePersona(): string {
    return this.activePersona;
  }

  public setPersona(name: string) {
    if (this.configs[name]) {
      this.activePersona = name;
    }
  }

  public getAttributes(): PersonaConfig {
    return this.configs[this.activePersona];
  }
}
