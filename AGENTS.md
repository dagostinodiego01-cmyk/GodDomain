# AGENTS.md — Rules for AI coding agents

Read this file and `Docs/CODING_STANDARDS.md` and `Docs/ARCHITECTURE.md` at the start of every session. If anything here conflicts with a user instruction, **ask** before proceeding.

## Project facts

- **Project:** GD (working title), Unreal Engine 5 + C++, multiplayer-ready action RPG.
- **Engine version:** Unreal Engine **5.8.4** (hotfix, 2026-10-20). Never assume APIs; names differ between engine versions. Do not open the project in 5.9 Preview.
- **Primary module:** `GodDomain` (project `Game/GodDomain.uproject`; class prefix `GodDomain`, e.g. `AGodDomainCharacter`).
- **Project origin:** UE 5.8 **Third Person template**, kept deliberately as a starting point. `Source/GodDomain/Variant_Combat|Variant_Platforming|Variant_SideScrolling/` is template scaffolding — do not build game systems inside it; new code goes in the folders listed in `Docs/ARCHITECTURE.md`.
- **Art tool:** Blender **5.3.0**. The MCP add-on requires Blender 5.1+. Installed as the **Steam** build at `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe` — not on `PATH` and not under `C:\Program Files\Blender Foundation`, so headless runs need the full path. Art direction: `Docs/ART_DIRECTION.md`; kit grid and textures: `Docs/ART_PIPELINE.md`.
- **Platform / IDE:** Windows 64-bit + Visual Studio 2022.
- **Agent tooling:** `.mcp.json` in the repo root wires the agent to the Unreal Editor (Unreal MCP, HTTP) and Blender (Blender Lab server, stdio). Setup, limits and safety: `Docs/MCP_SETUP.md`.
- **Build command:** `"<UE>/Engine/Build/BatchFiles/Build.bat" GodDomainEditor Win64 Development "<repo>/Game/GodDomain.uproject" -WaitMutex`. On this machine `<UE>` = `C:\Program Files\Epic Games\UE_5.8`.

## How to work

1. **Plan briefly, then change little.** Prefer small, focused diffs touching as few files as possible. Do not refactor unrelated code.
2. **Build after every change** and fix compile errors before moving on. Report the real compiler output; never claim a build passed without running it.
3. **Do not guess Unreal APIs.** If unsure a function, class or signature exists in this engine version, search the engine source (`Engine/Source`, `Engine/Plugins`) or say so. Wrong API calls are the most common failure here.
4. **State assumptions.** If a requirement is ambiguous, ask one short question or list the assumption you made.
5. **Explain non-obvious decisions** in a code comment or in `Docs/DECISIONS.md`.

## Hard rules (never do these without explicit approval)

- **Do not edit binary assets**: `*.uasset`, `*.umap`, `*.blend`, `*.fbx`, textures, audio. You cannot do this safely. Ask the user to make the Editor-side change and tell them exactly what to do.
- **Do not edit** `Config/*.ini`, `*.uproject`, `*.Build.cs`, or `*.Target.cs` without saying what changes and why. Do not enable or add plugins silently.
- **Do not delete** files, rename modules/classes used elsewhere, or change the project name.
- **Do not add third-party dependencies**, plugins or marketplace code without asking.
- **Do not commit** secrets, keys, or credentials, and never hard-code them.
- **Do not reuse names, characters, lore, or class names from other works** (including the novel that inspired the genre). Use the original naming in `Docs/DESIGN.md`. If unsure, ask.

## Code rules (short version — details in `Docs/CODING_STANDARDS.md`)

- **C++ first.** Gameplay logic goes in C++ so it is reviewable and diffable. Blueprints are thin wrappers (assigning assets, tuning values) only.
- **Data-driven.** No hard-coded balance numbers, item stats, prices, XP curves or class definitions in code. Use `UDataAsset` / `FTableRowBase` structs fed from `Data/*.csv`.
- **Multiplayer-ready from day one.** The server is authoritative for health, damage, cooldowns, inventory, currency and progression. Clients request; the server decides. Mark every replicated property and RPC deliberately.
- **Use GAS** (Gameplay Ability System) for stats, abilities, effects, cooldowns and tags. Do not build a parallel stat system.
- **Avoid `Tick`** unless justified; prefer timers, delegates and events.
- **Memory safety:** every `UObject*` member is a `UPROPERTY` (use `TObjectPtr<>`); use `TWeakObjectPtr` for non-owning references.
- Follow Unreal naming: `A` actors, `U` objects/components, `F` structs, `E` enums, `I` interfaces, `T` templates, `b` prefix for bools.
- Use project log categories (`LogGodDomain`, `LogGodDomainCombat`, etc.) instead of `UE_LOG(LogTemp, ...)`.

## Definition of done for any task

- [ ] Compiles cleanly in `Development Editor`
- [ ] No new warnings introduced
- [ ] No hard-coded balance values
- [ ] Replication behaviour stated (server/client/both) for new gameplay code
- [ ] Short note on how to test it in the Editor
- [ ] `Docs/` updated if architecture or a decision changed

## When you are stuck

Say what you tried, what the error is, and what you need from the user. Do not loop on the same fix more than twice.
