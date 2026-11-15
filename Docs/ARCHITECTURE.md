# Architecture

Status: **Proposed** — confirm in `DECISIONS.md` before building on it.

## Principles

1. **Multiplayer-ready, single-player first.** Write server-authoritative code from the start, even while testing offline. Retrofitting networking later is a rewrite.
2. **C++ first, data-driven.** Logic in C++, numbers in data (see below).
3. **GAS for everything stat-like.** Attributes, abilities, effects, cooldowns, tags.
4. **Small modules, clear ownership.** One system, one folder, minimal cross-dependencies.

## Required plugins

- Gameplay Abilities (GAS) — also add `GameplayAbilities`, `GameplayTags`, `GameplayTasks` to `GDomain.Build.cs`
- Enhanced Input

(Enable only what is needed. Record every addition in `DECISIONS.md`.)

## Source layout (`Game/Source/GDomain/`)

```
Core/        game mode, game state, player state, controller, log categories
Characters/  base character, player character, NPC base
Abilities/   GAS: attribute sets, ability base classes, effects, tags
Combat/      hit detection, damage pipeline, targeting, combos
Classes/     class definitions, promotion logic, skill unlocks
World/       interactables, zones, spawners, village systems
Economy/     items, inventory, currency, vendors, crafting (later)
UI/          HUD, widgets (view code only, no game rules)
Data/        row structs and data asset types
```

## Data-driven design

**Source of truth is text, not Editor assets**, so it can be reviewed, diffed and edited by an AI agent.

- Balance data lives in `Data/*.csv` (classes, skills, items, monsters, XP curves).
- In the Editor, import CSVs into `UDataTable` assets whose row structs derive from `FTableRowBase`.
- Content designers/agents change the CSV; a developer re-imports in the Editor.
- Complex per-entity assets (e.g. a class) may use `UPrimaryDataAsset`, but keep the numbers in CSV where possible.

Initial tables (all placeholders): `Classes.csv`, `ClassTiers.csv`, `Skills.csv`, `Monsters.csv`, `Items.csv`, `XPCurve.csv`.

## Class system model (draft)

```
ClassDefinition  (id, display name, role, base attribute growth)
  └─ PromotionNode (from class, to class, required level, quest id)
       └─ SkillUnlock (class, skill id, required level/tier)
```

- Classes form a **graph**: base class → promotion branches → hidden/special variants.
- Start with **one class, two tiers**; the structure must allow many more without code changes.
- Use original names (see `DESIGN.md`).

## Combat model (draft)

- **Hybrid action combat:** real-time movement, dodging and aiming; skills use forgiving, server-validated hit rules.
- Client predicts movement and ability activation; the **server validates hits and applies damage** via GAS effects.
- All damage flows through **one** pipeline (`Combat/`) so resistances, crits and buffs are applied consistently.
- Enemy danger scales in ranks that mirror player progression tiers (readable at a glance).

## Networking roadmap

| Stage | Model | Goal |
|---|---|---|
| 1 | Standalone (but replication-correct code) | Combat and class feel |
| 2 | Listen-server co-op (2–8 players) | Prove replication |
| 3 | Dedicated server | Hosting and persistence |
| 4 | Persistent shared world | Only if stages 1–3 are fun and viable |

Do not design for stage 4 yet.

## Art pipeline (Blender → Unreal)

1. Model and rig in `Art/Blender/`. One `.blend` per asset or small kit.
2. Export FBX/glTF to `Art/Exports/` using the agreed scale (1 Blender unit = 1 m; UE uses cm, so export with the correct unit scale).
3. Import into UE under a matching `Content/` folder; naming prefixes: `SM_` static mesh, `SK_` skeletal mesh, `M_` / `MI_` material, `T_` texture, `ABP_` anim blueprint, `AM_` montage.
4. Commit sources and exports together (both tracked via Git LFS).
5. Prefer a stylised, low-poly-friendly look so a solo artist can produce a village in weeks (see `DESIGN.md`).
