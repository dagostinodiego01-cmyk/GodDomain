# Decision Log

Format: **ID — Title — Status** (`Proposed` / `Accepted` / `Superseded`). Move decisions to *Accepted* only when confirmed by the project owner.

---

### ADR-001 — Unreal Engine 5.8 + C++ + Blender — Accepted
Chosen by the project owner as the stack. Engine version: **5.8**.

### ADR-002 — C++-first gameplay logic, Blueprints as thin wrappers — Proposed
**Why:** C++ is diffable and reviewable, and agents read and edit it reliably. MCP now lets agents touch Blueprint graphs too, but those changes are still binary and hard to review, so logic stays in C++.
**Trade-off:** slower iteration than Blueprints; mitigated by data-driven tuning.

### ADR-003 — Git + Git LFS for version control — Proposed
**Why:** free, simple, works with the agent tooling.
**Alternative:** Perforce, which handles large binary assets and exclusive checkout better. With assets now a source of truth and a possible second contributor, revisit this early (before M3). Check hosting LFS quotas before relying on them.

### ADR-004 — Hybrid source of truth — Accepted (revised)
Originally proposed: text/CSV for all data. **Revised** after the decision to use MCP agents in the editor.
**Decision:** C++, config and bulk balance tables are text (`Data/*.csv` → `UDataTable`); class/skill definitions, abilities, levels, materials, animation, UI and VFX are UE assets edited via MCP; Blender sources live in `Art/Blender/`. See `ARCHITECTURE.md`.
**Why:** MCP removes the main cost of assets-as-truth (agents could not edit them), but binary assets still cannot be diffed or merged, so reviewable content stays in text.
**Trade-off:** two places to look for data; mitigated by the table in `ARCHITECTURE.md`.

### ADR-005 — Multiplayer-ready, server-authoritative from day one — Proposed
**Why:** retrofitting networking is the biggest risk for the long-term MMO goal.
**Scope:** replication-correct code only; no dedicated-server work until M4+.

### ADR-006 — Gameplay Ability System for abilities, stats, effects — Proposed
**Why:** built for RPG attributes, cooldowns, buffs, replication and prediction.
**Trade-off:** steep learning curve and C++ boilerplate.

### ADR-007 — Original names and lore; do not reuse another work's IP — Proposed
See `DESIGN.md`.

### ADR-008 — MCP for agent access to Unreal Editor and Blender — Proposed
**Why:** lets agents do editor and content work directly instead of describing manual steps.
**Choice:** start with Epic's experimental Unreal MCP (5.8) and Blender's official MCP add-on; add third-party plugins only if a concrete gap appears, and record each one here.
**Risks:** experimental tooling, broad agent control of the project. Mitigations: local-only server, dev-only, checkpoint commits, rules in `AGENTS.md`, setup in `MCP_SETUP.md`.

### ADR-009 — Agent client: Freebuff (MCP-capable) — Proposed
**Why:** free, already known to support MCP (used previously with another engine).
**Fallback:** other MCP-capable agents. Keep nothing agent-specific in the repo except `AGENTS.md` and `MCP_SETUP.md`.

### ADR-010 — MCP client config: first-party servers only, pinned versions — Proposed
**Choice:** a single `.mcp.json` at the repo root declaring two servers — Epic's built-in **Unreal MCP** (HTTP, `http://127.0.0.1:8000/mcp`) with the **All Toolsets** plugin, and Blender's **Blender Lab** MCP server (stdio, launched with `uv` from a git clone). No third-party MCP plugin.
**Why:** both are maintained by the vendors of the tools we depend on, which keeps version drift and supply-chain risk down and avoids marketplace plugins that lag engine releases.
**Versions pinned:** Unreal Engine **5.8.4** (2026-10-20 hotfix), Blender **5.3.0** (2026-11-10). 5.9 is a Preview and not a baseline; upgrading is a deliberate decision, not a side effect of installing an agent tool.
**Trade-off:** Unreal MCP is declared experimental and its toolsets are thinner than some community offerings; if a concrete gap appears, add one plugin at a time and record it here (per `MCP_SETUP.md`).
**Risks:** broad agent control of editor and Blender content. Mitigated by loopback-only servers, dev-only plugins, checkpoint commits and the MCP rules in `Docs/AGENTS.md`.

### ADR-011 — Module named `GodDomain`; Third Person template kept; GAS wired — Accepted
**Module name:** the project was created as `GodDomain` (`GodDomain.uproject`, module `GodDomain`, targets `GodDomain` / `GodDomainEditor`), not `GDomain` as the early docs assumed. Docs now follow the project instead of renaming it: renaming a module later would break every include, `UCLASS` and `.uproject` reference for no functional gain. Class prefix is therefore `GodDomain` (`AGodDomainCharacter`), log categories `LogGodDomain*`.
**Template:** the UE 5.8 **Third Person** template (with `Variant_Combat`, `Variant_Platforming`, `Variant_SideScrolling`) was kept deliberately as a faster start rather than recreating a blank project. Its code is scaffolding: game systems do not go inside `Variant_*`; new code goes in the folders in `ARCHITECTURE.md`. The variants may be pruned once the real character exists.
**GAS wiring:** `GameplayAbilities` enabled in `Game/GodDomain.uproject`; `GameplayAbilities`, `GameplayTags`, `GameplayTasks` added to `GodDomain.Build.cs`. `GameplayTags`/`GameplayTasks` are engine runtime modules, not plugins, so they need no `.uproject` entry.
**Why:** GAS is the project-wide framework (ADR-006) and must be available before the first attribute set is written, otherwise a parallel stat system appears by accident.

---

## Template
```
### ADR-XXX — Title — Status
Why:
Trade-offs / alternatives:
```
