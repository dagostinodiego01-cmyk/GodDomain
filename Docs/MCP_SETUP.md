# MCP Setup — Unreal Editor and Blender

Status: **Draft.** Verify each step against Epic's and Blender's current documentation; the tooling is experimental and changes quickly.

## What MCP is used for here
Letting an AI agent (e.g. Freebuff) do **editor and content work** directly: inspect and edit assets, build levels, set up materials, run imports, and drive Blender. It is **not** used to write C++ (see `AGENTS.md`).

## Unreal Engine 5.8

1. Open the project in the Unreal Editor.
2. `Edit → Plugins`: enable **Unreal MCP** and the toolset plugin(s) it requires (guides name them differently, e.g. *All Toolsets* / *Editor Toolset*; check Epic's *Unreal MCP in Unreal Editor* page). Restart the editor.
3. Start the server, either by enabling **Auto Start Server** in Editor Preferences or with the console command `ModelContextProtocol.StartServer`.
4. Default endpoint: `http://127.0.0.1:8000/mcp` (port and path are configurable).
5. Generate or write the client config for your agent. Unreal can generate configs for some clients via the console command `ModelContextProtocol.GenerateClientConfig <Client>`.
6. **Freebuff config: `TODO`** — add the server as an MCP server in Freebuff's own configuration (HTTP transport, URL above). Record the exact steps here once working.
7. Launch the agent from the repository root so it picks up `AGENTS.md`.

Notes:
- By default the server may expose only a few discovery tools (list toolsets, describe toolset, call tool). The agent should discover available toolsets before acting.
- Third-party plugins (e.g. UEAgent, VibeUE, UE-MCP) extend the toolset. Add one **only** to fill a concrete gap, and record it in `DECISIONS.md`. Check licence, Windows/engine-version support and what it changes.

## Blender

1. Use Blender's **official MCP server/add-on** (requires Blender 5.1 or newer at time of writing) or a well-maintained community server. Record the choice in `DECISIONS.md`.
2. Install the add-on, enable it, and start the server from Blender.
3. Add the server to the agent's MCP configuration. **Freebuff config: `TODO`.**
4. Agents export to `Art/Exports/` (units: 1 Blender unit = 1 m; confirm UE import scale) and keep sources in `Art/Blender/`.

## Safety checklist
- [ ] Servers bind to `127.0.0.1` only. Do not forward or expose the ports.
- [ ] MCP and toolset plugins are **editor-only**; confirm they are not included in packaged builds.
- [ ] No tokens or credentials in committed config files (add local config to `.gitignore` if needed).
- [ ] Commit (or snapshot) **before** each agent session; review the change summary afterwards.
- [ ] Keep one editor session per project; avoid running two agents against the same project at once.
- [ ] Back up the project; experimental tooling can corrupt assets.

## Smoke test (do this once after setup)
1. Agent lists available toolsets/tools in the editor. 
2. Agent lists assets under `Content/` (read-only).
3. Agent creates a trivial test asset in `Content/Dev/`, reads it back, then you review and delete it.
4. Agent lists objects in a Blender scene (read-only), then exports a test cube to `Art/Exports/`.
5. Record any problems and fixes below.

## Known issues / notes
_(add as you go)_
