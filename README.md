# GD — Working Title

> Repository workspace for the generation of God's Domain. Working codename: **GD**; the public name is undecided (see `Docs/DESIGN.md`).

A fantasy **action RPG** being built solo (with possible help from a family member), with the long-term ambition of growing into a persistent online world featuring class progression, trade, commerce and city building.

**Status:** Pre-production. Greybox starter city (`LVL_StarterVillage_V3`) playable as a walk-through; combat not yet playable.

---

## Vision in one paragraph

Start small: a single **starter village** with one playable class, a combat system that feels good, and a handful of monsters. Prove the combat and class systems first, then add crafting and trade, then co-op multiplayer. A persistent MMO-scale world is a north star, **not** the first deliverable. See `Docs/ROADMAP.md`.

## Tech stack

| Area | Choice |
|---|---|
| Engine | Unreal Engine 5.8.4 (see `AGENTS.md`) |
| Gameplay code | C++ (Blueprints only as thin wrappers) |
| Ability / stat framework | Gameplay Ability System (GAS) |
| 3D modelling and rigging | Blender 5.3.0 |
| Version control | Git + Git LFS |
| Coding assistant | MCP-capable AI coding agents. Rules in `AGENTS.md` |

## Repository layout

```
.
├── README.md            ← you are here
├── AGENTS.md            ← rules for AI coding agents (read first!)
├── Docs/
│   ├── ARCHITECTURE.md  ← how the systems fit together
│   ├── CODING_STANDARDS.md
│   ├── DESIGN.md        ← pillars, scope, IP rules, open questions
│   ├── CITY_LAYOUT.md   ← governing city plan: wall, gates, districts, landmarks
│   ├── Layout/          ← plan drawing, level-vs-plan audit, V3 captures
│   ├── ART_DIRECTION.md ← the village look: palette, materials, districts
│   ├── ART_PIPELINE.md  ← Blender kit grid, textures, export/import
│   ├── MCP_SETUP.md     ← Unreal + Blender MCP setup
│   ├── ROADMAP.md       ← milestones and exit criteria
│   ├── TASK_CARDS.md    ← step-by-step cards for cheap-model agents
│   └── DECISIONS.md     ← log of technical decisions
├── Game/                ← the Unreal Engine project (.uproject lives here)
├── Art/
│   ├── Blender/         ← .blend source files
│   ├── Exports/         ← FBX/glTF for UE import, generated texture sheets
│   └── Reference/       ← reference images, mood boards
├── Data/                ← CSV/JSON source of truth for balance data
└── Tools/               ← helper scripts (Blender exporters, validators)
```

## Prerequisites

- Unreal Engine **5.8.4** via the Epic Games Launcher
- Visual Studio 2022 with the **"Game development with C++"** workload (Windows)
- Blender **5.3.0**
- Git and **Git LFS** (`git lfs install` once per machine)

## First-time setup

1. Clone the repo, run `git lfs install`, then `git lfs pull` (maps and assets are LFS objects).
2. Right-click `Game/GodDomain.uproject` → *Generate Visual Studio project files* (see `Game/README.md`).
3. Build the `Development Editor` target (command in `AGENTS.md`) and open the project. `LVL_StarterVillage_V3` is the startup map.
4. Optional: generate the base material sheets with `python Tools/Blender/generate_textures.py`.

## Day-to-day workflow

- Work in small, compilable steps. Commit after each one that builds.
- Gameplay logic lives in C++; balance numbers live in `Data/` (see `Docs/ARCHITECTURE.md`).
- Close the editor and do a full build after changing headers or adding `UCLASS`/`USTRUCT`/`UENUM` types. Live Coding is unreliable for these.
- Never commit secrets (API keys, server credentials).

## Working with an AI coding agent

Point the agent at `AGENTS.md` at the start of every session. If your tool does not read it automatically, paste: *"Read AGENTS.md and Docs/CODING_STANDARDS.md before doing anything."*

## Intellectual property note

This project is **inspired by** the genre conventions of VRMMO/LitRPG fiction but must not reuse any other work's names, characters, lore or class names. See `Docs/DESIGN.md`.

## Licence

Not yet decided. Treat all content as **All Rights Reserved** until a licence is added.
