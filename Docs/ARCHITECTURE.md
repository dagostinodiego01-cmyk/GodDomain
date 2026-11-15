# Architecture

Status: **Hybrid source-of-truth accepted** (see ADR-004). Other items remain *Proposed* in `DECISIONS.md`.

Engine: **Unreal Engine 5.8.4**. DCC: **Blender 5.3.0**.

Project file: `Game/GodDomain.uproject`, single runtime module `GodDomain`. Created from the UE 5.8 **Third Person template** (kept on purpose as a starting point); `Source/GodDomain/Variant_*` is scaffolding, not project code.

## Principles

1. **Multiplayer-ready, single-player first.** Write server-authoritative code from the start, even while testing offline. Retrofitting networking later is a rewrite.
2. **C++ first, data-driven.** Logic in C++, tuning in data, visual/spatial content in UE assets (see *Source of truth*).
3. **GAS for everything stat-like.** Attributes, abilities, effects, cooldowns, tags.
4. **Small modules, clear ownership.** One system, one folder, minimal cross-dependencies.

## Required plugins

- Gameplay Abilities (GAS) — **wired**: plugin enabled in `Game/GodDomain.uproject`; `GameplayAbilities`, `GameplayTags`, `GameplayTasks` added to `GodDomain.Build.cs`
- Enhanced Input
- Unreal MCP (Epic, declared experimental in 5.8) plus **All Toolsets**, which supplies the toolsets — **editor/dev only**, see `MCP_SETUP.md`

(Enable only what is needed. Record every addition in `DECISIONS.md`.)

## Source layout (`Game/Source/GodDomain/`)

`Core/` exists as of X-01 (log categories, game mode, game state, player state, player controller) and `Abilities/` as of M1-03 (attribute set, ability system bootstrap). Create each remaining folder with the first system that needs it; see ADR-022.

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

## Source of truth (hybrid)

Agents can work in the editor through MCP, so UE assets are first-class. But binary assets cannot be diffed or reviewed, so we split by content type:

| Content | Source of truth | Why |
|---|---|---|
| Gameplay logic, systems, networking | **C++** | Reviewable, diffable |
| Gameplay tags, project config | **Text** (`Config/*.ini`) | Diffable; changes need approval |
| Tabular balance data (XP curve, prices, monster stats, drop tables) | **`Data/*.csv`** → imported `UDataTable` | Easy to diff and rebalance in bulk |
| City layout (wall, gates, streets, blocks, landmark footprints, anchors) | **`Data/Layout/city_layout.csv`** → generated `Docs/Layout/CityPlan.svg` | Diffable, and `Tools/Layout/build_city_plan.py` checks it against the wall and the streets; the level is built *from* it, never the reverse |
| The layout audit | `Tools/Editor/compare_level_to_plan.py` | Measures every greybox actor's world bounds through MCP and compares them with `Data/Layout/city_layout.csv`; writes `Docs/Layout/Level_vs_Plan.md` (plan vs built vs delta, including the block array — count, per-row uniformity, party gap, pad clearance, frontage, pitch) and `Level_vs_Plan.svg` (both geometries on one 30 m grid, numbered pins with a measured legend). Run it after any setout rebuild |
| The evidence frames | `Tools/Editor/shoot_views.py` | Re-shoots arrival, gate, river, town and plan-grid frames from the live V3 level through `CaptureViewport`, and with `--pie` one frame from Play-In-Editor. Poses are in metres; the script converts to the editor's centimetres |
| The blockout level | `Game/Content/StarterVillage/LVL_StarterVillage_V3.umap` | Generated from the CSV by `Tools/Editor/build_level_v3.py` through the editor's MCP server — the editor authors the binary, the script never writes it. `DefaultEngine.ini` names it as both the game default map and the editor startup map. Its greybox meshes (`SM_Ground`, `SM_Stone`, `SM_Water`…) and their material instances live in `Content/StarterVillage/Greybox/{Meshes,Materials}` — one colour per category, so the setout reads in-engine |
| Class definitions, skill definitions | **UE data assets** (`UPrimaryDataAsset`) | Edited via MCP, typed references to abilities/effects |
| Abilities and effects (`GA_*`, `GE_*`) | **UE assets** (thin; logic in C++ base classes) | Standard GAS workflow |
| Levels, materials, animation, montages, VFX, UI layouts | **UE assets** | Inherently visual/spatial |
| Meshes, rigs, source animation | **Blender `.blend`** in `Art/Blender/` → exports in `Art/Exports/` | DCC source files |

Rules of thumb:
- If it is a **number that will be tuned in bulk**, it goes in a CSV.
- If it is **structure or references** (what a class unlocks, which ability a skill grants), it is a data asset.
- If it is **logic**, it is C++.
- Any asset an agent changes must be **read back and summarised** by the agent, then committed in a small checkpoint commit (see `AGENTS.md`).

Initial tables (placeholders): `ClassTiers.csv`, `Skills.csv`, `Monsters.csv`, `Items.csv`, `XPCurve.csv`.

## AI agents and MCP

- Agents connect to the **Unreal Editor** and **Blender** over local MCP servers. Details, setup and safety in `MCP_SETUP.md`.
- MCP is for **editor and content work** (assets, levels, materials, imports). **C++ is still written and compiled through the normal file + build workflow.**
- Prefer structured MCP tools over arbitrary Python execution. Raw Python in the editor is allowed only when stated to the user first.
- MCP servers are local-only and **dev-only**; they must never ship in a packaged build.
- Because the tooling is experimental, nothing in the game may *depend* on it at runtime, and everything it produces must remain editable by hand.

## Class system model (draft)

```
ClassDefinition  (UPrimaryDataAsset: id, display name, role; attribute growth curves from CSV)
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

Look: `ART_DIRECTION.md`. Kit grid, texture specs, phases: `ART_PIPELINE.md`.

0. Base materials are **generated, not painted**: `python Tools/Blender/generate_textures.py` writes tileable sheets to `Art/Exports/Textures/` from `Tools/Blender/palette.json`.
1. Model and rig in `Art/Blender/`. One `.blend` per asset or small kit.
2. Export FBX/glTF to `Art/Exports/` using the agreed scale (1 Blender unit = 1 m; UE uses cm, so export with the correct unit scale).
3. Import into UE under a matching `Content/` folder; naming prefixes: `SM_` static mesh, `SK_` skeletal mesh, `M_` / `MI_` material, `T_` texture, `ABP_` anim blueprint, `AM_` montage.
4. Commit sources and exports together (both tracked via Git LFS).
5. Prefer a stylised, low-poly-friendly look so a solo artist can produce a village in weeks (see `DESIGN.md`).
