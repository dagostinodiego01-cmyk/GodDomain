# Game/ — Unreal Engine 5 project root

**Project:** `GodDomain.uproject`
**Engine:** UE **5.8.4** — do not open it with a different engine version; asset upgrades are one-way.
**Module:** `GodDomain` (single runtime module; class prefix `GodDomain`, e.g. `AGodDomainCharacter`).

```
Game/
├── GodDomain.uproject
├── Config/
├── Content/
├── Source/
│   ├── GodDomain/            ← module: GodDomain.Build.cs, .cpp/.h
│   ├── GodDomain.Target.cs
│   └── GodDomainEditor.Target.cs
└── Plugins/                  ← create when the project gains its own plugin
```

## Origin: Third Person template (kept on purpose)

Created from the UE 5.8 **Third Person** template rather than a blank project, so movement, camera and animation already work. It ships three variants:

| Folder | What it contains |
|---|---|
| `Source/GodDomain/Variant_Combat/` | enemy AI, combat state-tree utility, danger/player env queries, UI |
| `Source/GodDomain/Variant_Platforming/` | platforming character + animation |
| `Source/GodDomain/Variant_SideScrolling/` | side-scrolling character, pickups, AI, UI |

These are **scaffolding**. Do not build game systems inside `Variant_*` — real code goes in the folders described in `Docs/ARCHITECTURE.md`. The variants can be pruned once our own character replaces them; nothing depends on them yet.

Content created by the template (maps, Blueprints, input assets) lives in `Content/` and is binary — change it through the editor (or MCP), never on disk.

## Enabled plugins

`ModelContextProtocol` + `AllToolsets` (agent access to the editor), `GameplayAbilities` (GAS), `StateTree`, `GameplayStateTree`, `ModelingToolsEditorMode`. See `Docs/MCP_SETUP.md` and ADR-011.

## Build

Close the editor before a full build — Live Coding cannot handle new `UCLASS`/`USTRUCT` types, and the editor locks the module DLL.

```
"C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" \
  GodDomainEditor Win64 Development "<repo>\Game\GodDomain.uproject" -WaitMutex
```

Open the `.uproject` (or `GodDomain.slnx`) to work in the editor. Project settings live in `Config/*.ini`; changes there need approval (see `AGENTS.md`).
