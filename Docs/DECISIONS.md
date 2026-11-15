# Decision Log

Format: **ID — Title — Status** (`Proposed` / `Accepted` / `Superseded`). Move decisions to *Accepted* only when confirmed by the project owner.

---

### ADR-001 — Unreal Engine 5 + C++ + Blender — Accepted
Chosen by the project owner as the stack.

### ADR-002 — C++-first gameplay logic, Blueprints as thin wrappers — Proposed
**Why:** AI coding agents can read and edit C++ but not Blueprint graphs (binary assets). C++ is also diffable and reviewable.
**Trade-off:** slower iteration than Blueprints; mitigated by data-driven tuning.

### ADR-003 — Git + Git LFS for version control — Proposed
**Why:** free, simple, works with the agent tooling.
**Alternative:** Perforce, which handles large binary assets and locking better. Revisit if repo size or asset conflicts become painful. Check hosting LFS quotas before relying on them.

### ADR-004 — Balance data in CSV/JSON under `Data/` — Proposed
**Why:** text source of truth that is diffable and editable by tools and agents; imported into `UDataTable` in the Editor.

### ADR-005 — Multiplayer-ready, server-authoritative from day one — Proposed
**Why:** retrofitting networking is the biggest risk for the long-term MMO goal.
**Scope:** replication-correct code only; no dedicated-server work until M4+.

### ADR-006 — Gameplay Ability System for abilities, stats, effects — Proposed
**Why:** built for RPG attributes, cooldowns, buffs, replication and prediction.
**Trade-off:** steep learning curve and C++ boilerplate.

### ADR-007 — Original names and lore; do not reuse another work's IP — Proposed
See `DESIGN.md`.

---

## Template
```
### ADR-XXX — Title — Status
Why:
Trade-offs / alternatives:
```
