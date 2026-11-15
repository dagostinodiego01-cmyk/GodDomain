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

_(add as you go)_
