# GD — Working Title

> Repository workspace for the generation of God's Domain. Working codename: **GD**; the public name is undecided (see `Docs/DESIGN.md`).

A fantasy **action RPG** being built solo (with possible help from a family member), with the long-term ambition of growing into a persistent online world featuring class progression, trade, commerce and city building.

**Status:** Pre-production. No playable build yet.

---

## Vision in one paragraph

Start small: a single **starter village** with one playable class, a combat system that feels good, and a handful of monsters. Prove the combat and class systems first, then add crafting and trade, then co-op multiplayer. A persistent MMO-scale world is a north star, **not** the first deliverable. See `Docs/ROADMAP.md`.

## Tech stack

| Area | Choice |
|---|---|
| Engine | Unreal Engine 5 (exact version recorded in `AGENTS.md`) |
| Gameplay code | C++ (Blueprints only as thin wrappers) |
| Ability / stat framework | Gameplay Ability System (GAS) |
| 3D modelling and rigging | Blender |
| Version control | Git + Git LFS |
| Coding assistant | AI coding agent (Freebuff / others). Rules in `AGENTS.md` |

## Repository layout

```
.
├── README.md            ← you are here
├── AGENTS.md            ← rules for AI coding agents (read first!)
├── Docs/
│   ├── ARCHITECTURE.md  ← how the systems fit together
│   ├── CODING_STANDARDS.md
│   ├── DESIGN.md        ← pillars, scope, IP rules, open questions
│   ├── ROADMAP.md       ← milestones and exit criteria
│   └── DECISIONS.md     ← log of technical decisions
├── Game/                ← the Unreal Engine project (.uproject lives here)
├── Art/
│   ├── Blender/         ← .blend source files
│   ├── Exports/         ← FBX/glTF ready for UE import
│   └── Reference/       ← reference images, mood boards
├── Data/                ← CSV/JSON source of truth for balance data
└── Tools/               ← helper scripts (Blender exporters, validators)
```

## Prerequisites

- Unreal Engine 5 via the Epic Games Launcher
- Visual Studio 2022 with the **"Game development with C++"** workload (Windows)
- Blender (current stable release)
- Git and **Git LFS** (`git lfs install` once per machine)

## First-time setup

1. Clone the repo and run `git lfs install`.
2. Create the Unreal C++ project inside `Game/` as described in `Game/README.md`.
3. Enable the plugins listed in `Docs/ARCHITECTURE.md` (Gameplay Abilities, Enhanced Input).
4. Generate Visual Studio project files (right-click the `.uproject`) and build the `Development Editor` target.
5. Commit the empty project as the first commit **before** adding any gameplay code.

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
