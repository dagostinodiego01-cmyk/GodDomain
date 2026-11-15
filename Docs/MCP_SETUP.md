# MCP Setup — Unreal Editor 5.8.4 and Blender 5.3.0

Status: **Checked against vendor documentation on 2026-11-15.** Both servers are first-party (Epic ships Unreal MCP inside the engine; Blender ships its MCP server under Blender Lab). No third-party plugin is in use — see ADR-010.

## Versions (pinned)

| Tool | Version | Why this one |
|---|---|---|
| Unreal Engine | **5.8.4** — hotfix, 2026-10-20, changelist 58902052 | Latest full release. 5.9 is a Preview built for the 2026 MegaJam and is explicitly not a baseline. |
| Blender | **5.3.0** — released 2026-11-10 | Current stable. The Blender Lab MCP add-on requires Blender 5.1 or newer. |

Do not open the project in a different engine version; asset upgrades are one-way.

## The config file

`.mcp.json` in the **repository root** declares both servers:

```json
{
  "mcpServers": {
    "unreal-mcp": { "type": "http", "url": "http://127.0.0.1:8000/mcp" },
    "blender": {
      "command": "uv",
      "args": ["--directory", "C:\\blender_mcp\\mcp", "run", "blender-mcp"]
    }
  }
}
```

- **Launch the agent from the repository root** so it picks up both `.mcp.json` and `AGENTS.md`.
- The Unreal entry is exactly what the engine's own generator writes, so it will keep working if you regenerate it.
- If Unreal writes its own `.mcp.json`, note where it lands: **project root for installed builds (`Game/`), engine workspace root for source builds**. Merge that entry into the root file and keep one config — do not maintain two.
- The Blender `--directory` path must match wherever you cloned the server (see below). It is a local machine path, not a secret, so committing it is fine.
- No tokens or credentials belong in this file. If a server ever needs a token, read it from an environment variable instead.

## Unreal Engine 5.8.4

1. Open the project in the **5.8.4** editor.
2. `Edit → Plugins`: enable **Unreal MCP** and **All Toolsets**. Unreal MCP is the server; the toolsets (actors, blueprints, materials, Niagara, Sequencer, GAS, …) come from All Toolsets, which needs to be enabled separately. **Toolset Registry** is enabled automatically as a dependency. Restart when prompted. (Already done in `Game/GodDomain.uproject` — both are enabled there.)
3. Start the server: `Edit → Editor Preferences → General → Model Context Protocol → Auto Start Server`, or run `ModelContextProtocol.StartServer` in the console. It binds `http://127.0.0.1:8000/mcp`; port and path are configurable in the same panel.
4. Optional: generate a client config with the console command `ModelContextProtocol.GenerateClientConfig <ClaudeCode|Cursor|VSCode|Gemini|Codex|All>`. JSON configs are merged with existing entries, so running it repeatedly is safe.
5. Confirm the Output Log shows the bind address, or check `LogModelContextProtocol`.

Behaviour worth knowing before you rely on it:

- **Tool search is on by default.** `tools/list` returns three meta-tools — `list_toolsets`, `describe_toolset`, `call_tool` — instead of every tool. Always discover a toolset and describe it before calling.
- **Calls run serially on the game thread.** Do not issue overlapping tool calls.
- **HTTP/SSE only.** No `stdio` or WebSocket transport.
- **Loopback only, no authentication.** Same-machine use only; never expose or forward the port.
- **Editor-only adapter.** Toolsets are not auto-discovered in cooked/shipping builds, even though the server modules are runtime modules.
- **Live Coding does not add new `UFUNCTION`s.** Adding a tool requires an editor restart; after authoring or hot-reloading toolsets run `ModelContextProtocol.RefreshTools`.
- Identifier and console prefix are `ModelContextProtocol`; the advertised name is `unreal-mcp`.
- `GASToolsets` (attribute sets, effects) is a separate experimental plugin, disabled by default. It is the one to look at when we start GAS work — enable it deliberately and record it in `DECISIONS.md`.

Debugging: `npx @modelcontextprotocol/inspector`, pointed at `http://127.0.0.1:8000/mcp` over Streamable HTTP, lists every tool and its schema and bypasses the agent's interpretation.

**Verified live 2026-11-15.** Editor logs `Engine Version: 5.8.4-58902052`; port 8000 `LISTENING` on `127.0.0.1`, owned by `UnrealEditor.exe`; `initialize` → HTTP 200, `protocolVersion` **2025-06-18**, `Mcp-Session-Id` issued; `tools/list` → the three meta-tools; `list_toolsets` → **52 toolsets**.

Toolsets that matter for this project:

- GAS — `GASToolsets.GameplayCueToolset`, `GASToolsets.AttributeSetToolset`, `GASToolsets.AbilitySystemInspectorToolset`, `GameplayTagsToolset.GameplayTagsToolset`
- Data — `editor_toolset.toolsets.data_table.DataTableTools` (our `Data/*.csv` → `UDataTable`), `data_asset.DataAssetTools` (class/skill definitions)
- Content — `actor.ActorTools`, `blueprint.BlueprintTools`, `material.MaterialTools`, `material_instance.MaterialInstanceTools`, `skeletal_mesh.SkeletalMeshTools`, `static_mesh.StaticMeshTools`, `scene.SceneTools`, `texture.TextureTools`
- UI / AI / animation — `UMGToolSet.UMGToolSet`, `BehaviorTreeTools`, `StateTreeTools`, `ControlRigTools`, `SequencerTools`
- Inspection — `EditorToolset.EditorAppToolset`, `EditorToolset.LogsToolset`, `ConfigSettingsToolset`

## Blender 5.3.0

Two parts are needed: an add-on inside Blender, and a small server process the agent launches.

1. **Add-on.** From blender.org/lab/mcp-server, drag the add-on link into Blender **twice** (first adds the Blender Lab repository, second installs it) — or download the zip and use *Install from Disk*. Current release: v1.0.3, requires Blender 5.1+.
2. **Server.** No pip step is needed; `uv` runs it straight from a clone:
   ```
   cd C:\
   git clone https://projects.blender.org/lab/blender_mcp.git
   ```
   On Windows that puts the server at `C:\blender_mcp\mcp`, which is the path in `.mcp.json`. If you clone elsewhere, update `--directory` to match.
   **Installed on this machine (2026-11-15):** cloned to `C:\blender_mcp`, so the committed path is correct. `uv` builds a local `.venv` inside the clone on first run (41 packages) — there is no global install and nothing on `PATH`.
3. **Start the bridge** in Blender from the add-on's preferences (or enable auto-start) and note the host/port it uses. The add-on talks to the server over a local TCP socket; keep it on `127.0.0.1`.
4. The agent starts the `blender-mcp` server itself. Do not launch it by hand as well.

**Name collision — read this before searching for a package.** Several different projects answer to "blender-mcp":

| What you see | What it actually is |
|---|---|
| `uvx blender-mcp` / PyPI `blender-mcp` | A **community** add-on (renamed to `mcp-for-blender`). Different add-on, different tools. Not what we use. |
| `blender-open-mcp` | Another community server. |
| **Blender Lab server** (this project) | The official one: clone from `projects.blender.org/lab/blender_mcp`, launched with `uv --directory <clone>/mcp run blender-mcp`. |

**Security.** Blender's own documentation warns that this server runs LLM-generated Python inside Blender with no guardrails protecting your data. Treat `Art/Blender/` accordingly: commit (or snapshot) before a session, work on copies when experimenting, and never point it at unrelated files on the machine.

## What MCP is for here

Editor and content work only: inspecting and editing assets, levels, materials, data assets, imports, and driving Blender. **C++ is not written through MCP** — edit source and build normally (see `AGENTS.md`).

## Safety checklist

- [ ] Servers bind to `127.0.0.1` only. Do not forward or expose the ports.
- [ ] MCP and toolset plugins are **editor/dev only**; confirm they are not enabled in a packaged build.
- [ ] No tokens or credentials in committed config files.
- [ ] Commit (or snapshot) **before** each agent session; review the change summary afterwards.
- [ ] One editor session per project; never run two agents against the same project at once.
- [ ] Back up the project; experimental tooling can corrupt assets.
- [ ] Close the editor before rebuilding after C++ header changes, and reopen it before resuming MCP work.

## Smoke test (once after setup)

1. Agent lists available toolsets, then describes one.
2. Agent lists assets under `Content/` (read-only).
3. Agent creates a trivial test asset in `Content/Dev/`, reads it back; you review and delete it.
4. Agent lists objects in a Blender scene (read-only), then exports a test cube to `Art/Exports/`.
5. Record any problems and fixes below.

## Known issues / notes

**Blender side verified working 2026-11-15.** Add-on bridge listening on `127.0.0.1:9876` (owned by `blender.exe`), MCP handshake completed, **26 tools** advertised, and a live read-only call (`get_blendfile_summary_datablocks`) returned real scene data — 35 data-blocks, EEVEE, scene `Scene`, active workspace `Scripting`.

- **Port collision to avoid.** The server's optional HTTP transport defaults to `--port 8000`, the same port Unreal MCP uses. If you ever switch Blender to HTTP, pass a different port and keep the two apart. We use stdio, so this does not apply to the committed config.
- **`execute_blender_code` / `execute_blender_code_for_cli` exist.** These run arbitrary Python inside Blender. Per `Docs/AGENTS.md`, say what the code does and get agreement before running it; prefer the structured tools.
- **Plain vs `_for_cli` tools.** Most read tools have a `_for_cli` twin; the plain variant expects a live Blender UI session, the twin works headless.
- **stdin EOF is not a failure.** The stdio server exits with code 0 when its stdin closes. That is normal; do not read it as a crash.
- **Cosmetic version mismatch.** `serverInfo` reports `1.30.0` while `mcp/pyproject.toml` says `1.0.2`. Harmless, but trust the clone's git commit when reporting a version.
- **Unreal side verified 2026-11-15** — see the block in the Unreal section above. `serverInfo` comes back with `name`, `title` and `version` as **empty strings**; cosmetic, but a client that displays the server name shows it blank. MCP still cannot write C++, by design and by rule.
- **Greybox workflow (proven 2026-11-15).** No structured "create level" tool exists: duplicate `/Engine/Maps/Templates/Template_Default` into the project, `save_assets`, then `load_level` (a fresh duplicate must be saved before it loads). Drive bulk placement through `execute_tool_script` — sandboxed, can only call registered tools, no `unreal` module access.
- **Building a level from the plan (proven 2026-11-15).** `Tools/Editor/ue_mcp.py` is a small client for this server (`list`, `toolsets`, `describe <toolset>`, `call <toolset> <tool> <json>`); it handles the handshake, the `Mcp-Session-Id` header and the event-stream framing. `Tools/Editor/build_level_v3.py` turns `Data/Layout/city_layout.csv` into `LVL_StarterVillage_V3`: one blockout actor per CSV primitive, in outliner folders under `GD/Greybox`. Dry run by default; `--apply` spawns, `--clear` wipes `GD/Greybox` first so a re-run is idempotent. It refuses to run unless the target level is the open one.
- **PIE blocks scene tools.** While a Play-In-Editor session runs, `get_current_level` returns `""` and `LevelEditorSubsystem` logs "The Editor is currently in a play mode." Stop PIE (or wait for the user to) before placing actors. `EditorAppToolset.IsPIERunning` answers the question without guessing.
- **`CaptureViewport` needs `annotations`.** Call it with `captureTransform` *and* the full annotations object (`gridSpacing`, `gridExtent`, `gridHeight`, `maxLabelDistance`, `classFilter: null`, `maxLabels`); without annotations it returns `null` and `isError`. Pitch −90 exactly also returns null — use −89.9. The image comes back as `returnValue.image.data`, base64 PNG. `CaptureEditorImage` takes no arguments and returns `returnValue.{mimeType,data}` directly — a different shape; it captures the viewport as-is, UI and all, which is how a Play-In-Editor frame gets recorded.
- **`StartPIE` requires its `options` object** — `{bSimulate, playMode, warmupSeconds}` are all required or the call is rejected before it starts. `playMode: PlayMode_InViewPort` keeps the game in the main viewport, which is what `CaptureEditorImage` needs.
- **The startup map now opens V3.** `DefaultEngine.ini` sets `EditorStartupMap` to `LVL_StarterVillage_V3`, so after an editor restart the level is already open — the build script's "open the right level" step usually has nothing to do.
- **Invocation rules learned the hard way.** In tool-search mode, real tools go through `call_tool` with `toolset_name` + bare `tool_name`; omit `arguments` for no-arg tools. Actor `refPath`s carry internal `UAID` names, not labels — relocate by label via `find_actors`, never by parsing refs. `DefaultGame.ini` gets a 5.8 schema rewrite by the editor on first map load — keep it, don't revert.
- **Visual verification works (proven 2026-11-15).** `CaptureViewport` with `captureTransform` + full `annotations` (`gridSpacing`, `gridExtent`, `gridHeight`, `maxLabelDistance`, `classFilter` which may be `null`, `maxLabels`) returns `returnValue.image.{mimeType, data}` — a base64 PNG rendered from the given pose with actor labels, independent of the user's viewport camera. `bShowUI: false` hides gizmos. `CaptureEditorImage` captures the user's viewport as-is (no pose control); its PNG may exceed attachment size limits, so downscale before viewing.

- **Batch with `ProgrammaticToolset.execute_tool_script` (proven 2026-11-15).** The server exposes `editor_toolset.toolsets.programmatic.ProgrammaticToolset.execute_tool_script({script})`: a sandboxed Python script that defines `run()` and calls any registered tool through `execute_tool(name, json_string)`. Modules are limited to `json`, `math`, `time`, `datetime`, `copy`, `re`. One call that loops over a JSON list of actor parameters spawned 494 actors in seconds — the same build one-actor-per-call takes ~20 minutes, because each MCP round trip costs ~1 s. Use it for any bulk pass: spawn, clear (`get_actors_in_folder` + `remove_from_scene`), or folder assignment.
- **Materials: instance, then mesh variant (proven 2026-11-15).** `MaterialInstanceTools.create(folder, asset_name, parent)` with parent `/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial`, then `set_vector_parameter(instance, "Color", {r,g,b,a})` and `set_scalar_parameter(instance, "Roughness", v)`. That parent has exactly two parameters: `Color` and `Roughness`. Actors take a **mesh asset**, not a material, so assign colour by duplicating the primitive: `AssetTools.duplicate({path, new_path})` then `StaticMeshTools.set_material({mesh, slot_name, material})` on the copy, and point the builder at the copy. Eight categories cost eight duplicates and eight material instances.
- **Slot names differ per primitive.** The engine cube's slot is `WorldGridMaterial`; the cylinder's and sphere's are `DefaultMaterial`. Read `StaticMeshTools.get_material_slots` first instead of assuming.
- **`save_assets` wants asset paths, not folders.** Passing `/Game/.../Meshes` logs `Could not load asset: .../Meshes.Meshes` and saves nothing; pass each `/Game/.../SM_X.SM_X`, or the level path.
- **Captures are too big to read at full size** (~800 KB–1.2 MB PNG). `Tools/Editor/resize_shot.ps1 -In <png> -Out <jpg> -Width 900` downscales to a viewable JPEG with System.Drawing (no ImageMagick or PIL on this machine). This machine blocks unsigned scripts, so call it as `powershell -NoProfile -ExecutionPolicy Bypass -File ...`.
- **Evidence frames are a script, not a ritual.** `Tools/Editor/shoot_views.py` re-shoots arrival, gate, river, town and the plan grid from the live level, and `--pie` adds one from Play-In-Editor; poses are written in metres and converted to the editor's centimetres. Use it after any rebuild instead of rebuilding the calls by hand.
- **A straight-down capture is not north-up.** The axes are left-handed, so a camera looking down at yaw 90 puts east on the **left** (a mirror of the plan) while yaw 270 puts east on the right with **south at the top** — the plan turned 180°, which is the honest one. `Level_Top_V3.png` is shot at yaw 270 for that reason; check `WorldPosToScreenCoords` instead of eyeballing an orientation.
- **A block's `count` is its building count.** Share it across the block's rows (`divmod`) rather than rounding per row: with `round(count / 2)` a 13-plot block came out as 12 and the town was five buildings short of the plan's 300, which no shape check would ever catch — only the count did.
- **Anything placed across a water channel must be cut, not laid over it.** A street pad is a 10 cm slab; left whole it lids the river at ground level and the bridge, both banks and the water vanish from the arrival shot. `build_level_v3.py` clips every street polyline against the river band and the stream slot before emitting pads.

_(add as you go)_
