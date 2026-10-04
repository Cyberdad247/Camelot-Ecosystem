# Document ID: BRAND-INTEGRATION-v1
**Status:** PROPOSED & IMPLEMENTED  
**Authority Layer:** L2 (brand + experience)  
**Owner:** experience.team + business.owner  
**Extends:** VS-014 (experience-plane), DESIGN-SYSTEM.md, ASSET-MANIFEST.md  
**Date:** 2026-10-04  

---

## I. Asset Inventory & Role Definition

| Image Asset | Name / Role | Visual Aesthetic & Motifs | Brand Story & Function |
| :--- | :--- | :--- | :--- |
| **Image 1** | **"KNIGHTS OF THE ROUND"**<br>(Hero) | Cyber-medieval: chrome knights, obsidian palace, cyan network mesh. | Full-viewport landing hero for Camelot-OS. The search bar at bottom maps directly to `.search-container`. |
| **Image 2** | **Invisioned Marketing**<br>(Parent Logo) | Corporate silhouette, purple (`#8B5CF6`) + gold (`#D4AF37`), skyline. | Parent umbrella company ("Business Consulting etc."). The commercial, IP, and legal holder. |
| **Image 3** | **Invisioned Marketing / Agentic Systems**<br>(Division Logo) | Golden knight helmet, purple circular aura, city skyline. | Agentic Systems Consulting division mark. Sits between Invisioned and Camelot-OS. |
| **Image 4** | **Camelot-OS Crest**<br>(Product Mark) | Circuit-board shield, dragon flourishes, tech-crown, cyan wireframe. | The product mark and kernel fortification shield. |

*Disposition Note on Crest:* AI-rendered pseudo-text in the crest footer is treated as decorative brand language, not system state (per `INV-010`).

---

## II. Brand Hierarchy Tree

```text
Invisioned Marketing Inc.                  [Corporate parent]
│
├── Business Consulting etc.             [Existing commercial practice]
│
└── Agentic Systems Consulting           [Cognitive systems practice — CAMELOT lives here]
    │
    └── Camelot-OS                       [The sovereign operating system product]
        │
        ├── Camelot-VPS                  [The kernel host]
        ├── HIVE Engineering Plane       [The delivery practice]
        ├── World Tree                   [The immersive projection]
        ├── Ecoshell                     [The operator shell]
        ├── HTMX Docs                    [This project]
        └── Slices VS-001..VS-031        [The work units]
```

---

## III. Formal Design Tokens

```css
:root {
  /* Corporate parent — Invisioned Marketing */
  --im-purple:        #8B5CF6;  /* primary brand purple */
  --im-purple-deep:   #5B21B6;  /* shadow */
  --im-gold:          #D4AF37;  /* accent gold */
  --im-gold-bright:   #E6C068;  /* highlight */
  --im-black:         #0A0A0A;

  /* Product — Camelot-OS */
  --obsidian-void:    #050505;  /* primary background */
  --luxora-gold:      #D4AF37;  /* matches im-gold */
  --matrix-cyan:      #00E5FF;  /* mesh, wireframe, live signal */
  --chrome-silver:    #C8CDD4;  /* knight plating, neutral text */
  --circuit-violet:   #7C3AED;  /* crest circuit traces */

  /* Semantic */
  --capability-local: var(--im-gold);      /* local-only mode */
  --capability-cloud: var(--matrix-cyan);  /* local+cloud mode */
  --signal-active:    var(--matrix-cyan);
  --signal-warn:      #E6B84D;
  --signal-error:     #E05252;
  --signal-ok:        #6EC07A;
}
```

### Typography Rules
* **Camelot Title:** Engraved old-style serif — Google Fonts: **`Cinzel`** (700/800 weight).
* **Headings & Body:** System sans / Inter.
* **Code & Monospace:** `JetBrains Mono` / `ui-monospace`.
* **Constraint:** The script "invisioned" font is never used inside Camelot-OS UI (belongs exclusively to the parent corporate mark). Camelot uses engraved serif + sans + monospace.
