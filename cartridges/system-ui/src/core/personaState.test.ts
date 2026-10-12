import { describe, expect, it } from 'vitest';
import { PersonaStateManager } from './personaState';

describe('PersonaStateManager', () => {
  it('should change active character profile and fetch corresponding attributes', () => {
    const manager = new PersonaStateManager();
    expect(manager.getActivePersona()).toBe('Anya');

    manager.setPersona('Merlin');
    expect(manager.getActivePersona()).toBe('Merlin');
    expect(manager.getAttributes().emotion).toBe('LOGIC_STRICT');
  });
});
