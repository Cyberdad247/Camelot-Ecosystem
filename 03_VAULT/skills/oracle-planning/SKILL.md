| name | description |
| :--- | :--- |
| oracle-planning | Sovereign Task DAG decomposition and Risk Protocol |

# Oracle Planning Skill

**Role:** Kernel Planning (L3) & Decomposition.

Use this skill when initiating any complex directive to ensure deterministic execution paths.

## Phase 1: Context Absorption

1. **Source Audit**: Identify all influencing UKG nodes, local files, and USER requirements.
2. **Boundary Check**: Consult `docs/TITANIUM_LAWS.md` and `docs/EMPIRE_MAP.md` for constraints.

## Phase 2: DAG Decomposition

1. **Role Mapping**: Decompose the task into discrete nodes for each active Lens:
   - **[PLAN]**: Strategic decomposition.
   - **[CODE]**: Implementation blocks.
   - **[SECURITY]**: Policy enforcement & Audit.
   - **[TEST]**: Verification & Sandbox execution.
2. **Dependency Mapping**: Clearly define the order of execution (Task DAG).

## Phase 3: Risk Assessment

1. **Side-Effect Matrix**: Identify potential conflicts with existing modules.
2. **Assumption Logging**: Document any "truths" being assumed during planning.
3. **Iron Gate Check**: Flag any operations requiring `requires_approval: true` (>10 lines, DELETE, EXECUTE).

## Phase 4: Implementation Plan Artifact

- Generate a compact **Implementation Plan** (Table/JSON) to be reviewed by the Operator.

---
*Created by Merlin_Omega for the Camelot-OS Skills Vault (03_VAULT).*
