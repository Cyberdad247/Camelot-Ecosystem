| name | description |
| :--- | :--- |
| browser-forensics | Nano-Knights Forensic DOM Analysis & Sentry Operations |

# Browser Forensics Skill

**Role:** Nano-Knight (Swarm) & Web Audit.

Use this skill to deploy the Nano-Browser swarm for automated UI/UX analysis and forensic scraping.

## Phase 1: Swarm Deployment

1. **Manifest Alignment**: Ensure the Nano-Browser environment (MV3) is configured for the target.
2. **Content Sentry Hook**: Initialize `content_sentry.js` to protect against injection.

## Phase 2: DOM Forensic Mapping

1. **Tree Traversal**: Use `buildDomTree.js` to extract semantic meaning from the page structure.
2. **Visual QA**: Capture screenshots and trace event handlers for interactive elements.

## Phase 3: Extraction & Audit

1. **Data Cleaning**: Filter out ephemeral UI noise and focus on "Target Assets."
2. **Security Audit**: Scan for trackers, unauthenticated API calls, or leaky client-side state.

## Phase 4: Synthesis

- Return the **Forensic Data Packet** (JSON) to the Chronos/Semantic layer for UKG ingestion.

---
*Created by Merlin_Ω for the Camelot-OS Skills Vault (03_VAULT).*
