// SPDX-License-Identifier: MIT

import { ROUND_TABLE } from './personas.js';

/**
 * Knight Spawner: Multi-Identity Swarm Manager
 * Coordinates launching parallel authenticated sessions
 */

export class KnightSpawner {
    constructor(profileManager) {
        this.profileManager = profileManager;
        this.activeSquads = new Map(); // squadId -> [tabIds]
    }

    /**
     * Deploy a Squad for a research mission
     * @param {string} missionGoal
     * @param {Array<string>} [roster] - Optional list of Persona IDs
     */
    async deploySquad(missionGoal, roster = ['LADY_APIS', 'SIR_SYNTAX', 'SIR_ZENITH']) {
        console.log(`[SPAWNER] Deploying Squad for: ${missionGoal}`);
        const squadId = crypto.randomUUID();

        // Define Squad Configuration based on Roster
        const squadConfig = roster.map(knightId => {
            const knight = ROUND_TABLE[knightId];
            return {
                role: knight.name,
                profile: knight.profile_bias,
                task: `${knight.title} - ${missionGoal}`,
                personaId: knightId
            };
        });

        const squadTabs = [];

        for (const unit of squadConfig) {
            // 1. Create Tab
            const tab = await chrome.tabs.create({ url: 'about:blank', active: false });
            squadTabs.push(tab.id);

            // 2. Inject Identity (Stealth + Persona)
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: (pid, role, personaId) => {
                    sessionStorage.setItem('NANO_PROFILE_ID', pid);
                    sessionStorage.setItem('NANO_ROLE', role);
                    sessionStorage.setItem('NANO_PERSONA_ID', personaId);
                    console.log(`[KNIGHT] Assigned Identity: ${pid} as ${role}`);
                },
                args: [unit.profile, unit.role, unit.personaId]
            });
        }

        this.activeSquads.set(squadId, squadTabs);

        return {
            squadId,
            conf: squadConfig,
            tabIds: squadTabs
        };
    }

    /**
     * Handoff a mission to a different Persona (e.g. on Block)
     * @param {number} oldTabId
     * @param {string} newPersonaId
     */
    async handoff(oldTabId, newPersonaId) {
        console.log(`[SPAWNER] Initiating Handoff for Tab ${oldTabId} -> ${newPersonaId}`);
        const knight = ROUND_TABLE[newPersonaId];
        if (!knight) throw new Error("Unknown Persona");

        // 1. Get State
        const oldTab = await chrome.tabs.get(oldTabId);
        const url = oldTab.url;

        // 2. Close Old Tab
        await chrome.tabs.remove(oldTabId);

        // 3. Spawn New Tab (Fresh Identity)
        const newTab = await chrome.tabs.create({ url: 'about:blank', active: true });

        // 4. Inject New Persona
        await chrome.scripting.executeScript({
            target: { tabId: newTab.id },
            func: (pid, role, personaId) => {
                sessionStorage.clear();
                sessionStorage.setItem('NANO_PROFILE_ID', pid);
                sessionStorage.setItem('NANO_ROLE', role);
                sessionStorage.setItem('NANO_PERSONA_ID', personaId);
                console.log(`[KNIGHT] Handoff Complete: ${role} taking over.`);
            },
            args: [knight.profile_bias, knight.name, newPersonaId]
        });

        // 5. Navigate
        await chrome.tabs.update(newTab.id, { url: url });

        return newTab.id;
    }

    /**
     * Terminate a squad
     */
    async dismissSquad(squadId) {
        const tabs = this.activeSquads.get(squadId);
        if (tabs) {
            await chrome.tabs.remove(tabs);
            this.activeSquads.delete(squadId);
            console.log(`[SPAWNER] Squad ${squadId} dismissed.`);
        }
    }
}
