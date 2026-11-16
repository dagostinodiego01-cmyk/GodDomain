# Decision Log

Format: **ID — Title — Status** (`Proposed` / `Accepted` / `Superseded`). Move decisions to *Accepted* only when confirmed by the project owner.

---

### ADR-001 — Unreal Engine 5.8 + C++ + Blender — Accepted
Chosen by the project owner as the stack. Engine version: **5.8**.

### ADR-002 — C++-first gameplay logic, Blueprints as thin wrappers — Proposed
**Why:** C++ is diffable and reviewable, and agents read and edit it reliably. MCP now lets agents touch Blueprint graphs too, but those changes are still binary and hard to review, so logic stays in C++.
**Trade-off:** slower iteration than Blueprints; mitigated by data-driven tuning.

### ADR-003 — Git + Git LFS for version control — Proposed
**Why:** free, simple, works with the agent tooling.
**Alternative:** Perforce, which handles large binary assets and exclusive checkout better. With assets now a source of truth and a possible second contributor, revisit this early (before M3). Check hosting LFS quotas before relying on them.

### ADR-004 — Hybrid source of truth — Accepted (revised)
Originally proposed: text/CSV for all data. **Revised** after the decision to use MCP agents in the editor.
**Decision:** C++, config and bulk balance tables are text (`Data/*.csv` → `UDataTable`); class/skill definitions, abilities, levels, materials, animation, UI and VFX are UE assets edited via MCP; Blender sources live in `Art/Blender/`. See `ARCHITECTURE.md`.
**Why:** MCP removes the main cost of assets-as-truth (agents could not edit them), but binary assets still cannot be diffed or merged, so reviewable content stays in text.
**Trade-off:** two places to look for data; mitigated by the table in `ARCHITECTURE.md`.

### ADR-005 — Multiplayer-ready, server-authoritative from day one — Proposed
**Why:** retrofitting networking is the biggest risk for the long-term MMO goal.
**Scope:** replication-correct code only; no dedicated-server work until M4+.

### ADR-006 — Gameplay Ability System for abilities, stats, effects — Proposed
**Why:** built for RPG attributes, cooldowns, buffs, replication and prediction.
**Trade-off:** steep learning curve and C++ boilerplate.

### ADR-007 — Original names and lore; do not reuse another work's IP — Proposed
See `DESIGN.md`.

### ADR-008 — MCP for agent access to Unreal Editor and Blender — Proposed
**Why:** lets agents do editor and content work directly instead of describing manual steps.
**Choice:** start with Epic's experimental Unreal MCP (5.8) and Blender's official MCP add-on; add third-party plugins only if a concrete gap appears, and record each one here.
**Risks:** experimental tooling, broad agent control of the project. Mitigations: local-only server, dev-only, checkpoint commits, rules in `AGENTS.md`, setup in `MCP_SETUP.md`.

### ADR-009 — Agent client: Freebuff (MCP-capable) — Proposed
**Why:** free, already known to support MCP (used previously with another engine).
**Fallback:** other MCP-capable agents. Keep nothing agent-specific in the repo except `AGENTS.md` and `MCP_SETUP.md`.

### ADR-010 — MCP client config: first-party servers only, pinned versions — Proposed
**Choice:** a single `.mcp.json` at the repo root declaring two servers — Epic's built-in **Unreal MCP** (HTTP, `http://127.0.0.1:8000/mcp`) with the **All Toolsets** plugin, and Blender's **Blender Lab** MCP server (stdio, launched with `uv` from a git clone). No third-party MCP plugin.
**Why:** both are maintained by the vendors of the tools we depend on, which keeps version drift and supply-chain risk down and avoids marketplace plugins that lag engine releases.
**Versions pinned:** Unreal Engine **5.8.4** (2026-10-20 hotfix), Blender **5.3.0** (2026-11-10). 5.9 is a Preview and not a baseline; upgrading is a deliberate decision, not a side effect of installing an agent tool.
**Trade-off:** Unreal MCP is declared experimental and its toolsets are thinner than some community offerings; if a concrete gap appears, add one plugin at a time and record it here (per `MCP_SETUP.md`).
**Risks:** broad agent control of editor and Blender content. Mitigated by loopback-only servers, dev-only plugins, checkpoint commits and the MCP rules in `Docs/AGENTS.md`.

### ADR-011 — Module named `GodDomain`; Third Person template kept; GAS wired — Accepted
**Module name:** the project was created as `GodDomain` (`GodDomain.uproject`, module `GodDomain`, targets `GodDomain` / `GodDomainEditor`), not `GDomain` as the early docs assumed. Docs now follow the project instead of renaming it: renaming a module later would break every include, `UCLASS` and `.uproject` reference for no functional gain. Class prefix is therefore `GodDomain` (`AGodDomainCharacter`), log categories `LogGodDomain*`.
**Template:** the UE 5.8 **Third Person** template (with `Variant_Combat`, `Variant_Platforming`, `Variant_SideScrolling`) was kept deliberately as a faster start rather than recreating a blank project. Its code is scaffolding: game systems do not go inside `Variant_*`; new code goes in the folders in `ARCHITECTURE.md`. The variants may be pruned once the real character exists.
**GAS wiring:** `GameplayAbilities` enabled in `Game/GodDomain.uproject`; `GameplayAbilities`, `GameplayTags`, `GameplayTasks` added to `GodDomain.Build.cs`. `GameplayTags`/`GameplayTasks` are engine runtime modules, not plugins, so they need no `.uproject` entry.
**Why:** GAS is the project-wide framework (ADR-006) and must be available before the first attribute set is written, otherwise a parallel stat system appears by accident.

### ADR-012 — Starter town greybox via Unreal MCP; provisional functional names — Accepted
**What:** `Game/Content/StarterVillage/LVL_StarterVillage.umap` (148 KB, single file, not world-partitioned) — duplicated from engine `Template_Default`, then populated with **52 greybox actors**: ground slab, cross roads, plaza + fountain, town hall, 6 market stalls, 4 shops, auction hall + tower + courtyard, 10 old-town blocks, archive, 4 gate towers, 2 fields, 2 barns, windmill, 12 tree-ring cones, one PlayerStart. Saved, verified by read-back (52 actors, bounds match the plan), camera parked for an aerial view.
**Names:** every label is functional (`GB_TownHall`, `GB_Slum_03`, …) — no proper nouns, so nothing collides with the IP rule. Final district and place names are still TBD in `DESIGN.md`.
**Conventions set:** level assets use the `LVL_` prefix; greybox actors live under `Greybox/*` outliner folders.
**Method note:** `execute_tool_script` runs sandboxed Python that can only call registered MCP tools (no `unreal` module access) — batched structured tools, not raw editor scripting. In tool-search mode every real tool goes through `call_tool` with `toolset_name` + bare `tool_name`. Actor `refPath`s carry internal `UAID` names, not labels — relocate actors by label via `find_actors`, never by parsing refs.

### ADR-013 — Starter town v2: river town on terraces — Superseded
**Superseded by `CITY_LAYOUT.md` revision C (ADR-025):** one river outside the south wall, a stream outside the east wall, a flat town inside; built as `LVL_StarterVillage_V3`. Kept below as history.
**What:** `Game/Content/StarterVillage/LVL_StarterVillage_V2.umap`, built after the owner supplied a concept reference. `LVL_StarterVillage` (ADR-012) is left untouched for comparison.
**Structure:** 140 m-wide river corridor dropping 8.5 m below the quay top; six terraces on both banks (E 2.5 / 6 / 10 / 15 m, W 3 / 9 m); stone quays; three stair flights of seven steps; two arched bridges with 15 m piers; 106 houses packed at 19–33 m spacing in three bands around a clock tower and a buttressed church; four docks, four boats, 48 trees, plaza with fountain, PlayerStart on the plaza. 192 actors, eight `Greybox/*` folders, saved and visually verified from a pose-specified viewport capture.
**Why the rebuild:** the first blockout was a crossroads on a flat slab — the reference is a river town on a slope. The decisive variable turned out to be **density**: houses at 80–90 m spacing read as scattered farms at any camera distance; the same buildings at 19–33 m read as a town. Building count matters far less than spacing.
**Still missing (track B, art):** every surface is default grey. Water, roofs, timber, stone and foliage have no materials, so any capture reads as untextured blocks. Nothing here is a lighting or material judgement yet.

**Folder convention, revised:** in a level that is *entirely* greybox, the `Greybox/` prefix is redundant. `LVL_StarterVillage_V2` therefore groups by district at the root (`Town/District_*`, `Town/Streets`, `Terrain`, `Water`, `Wilds`, `Gameplay`). Keep the `Greybox/` prefix for any level that mixes final art with blockout.

### ADR-014 — Five districts with distinct character — Accepted (extents superseded)
**Partly superseded by `CITY_LAYOUT.md` revision C:** the five districts and their character stand; positions, extents and heights are now in `CITY_LAYOUT.md` §5, the cathedral (not the town hall) is the tallest silhouette, and the parish church below is merged into the cathedral precinct as the cloister — the town has one spire.
**What:** the town inside `LVL_StarterVillage_V2` is a walled ring (200 m radius, 20 segments, four gate towers) around a central plaza, divided into five districts that must read as different places from a distance and at street level.

| District | Position | Character | Greybox signature |
|---|---|---|---|
| **Town Hall** | north of the plaza | grand, luxurious, civic power | tallest silhouette (32 m tower + 16 m spire), podium, colonnade wings, ceremonial steps onto the plaza |
| **Trade District** | west, between plaza and west gate | busy, commercial, crowded | densest rows (28 shops in four ranks), 9–13.5 m, awning-height roofs, stalls ringing the plaza |
| **Auction House** | east, inside its own walled courtyard | singular, wealthy, a landmark | round hall with domed roof, detached spire tower, U-shaped courtyard wall |
| **The Slums** | south, against the wall | worn, sad, cramped | lowest and smallest buildings (3.5–5.9 m), irregular yaw, lean-to roofs, alley shacks between rows |
| **Library** | south-east, adjoining the slums | old, apart, scholarly | isolated walled plot, buttressed nave, tall spire tower, separated from the slums by a plot wall |

**Why:** district identity is carried by **silhouette, height and density first**, materials second. A player on the plaza should be able to tell where they are from roofline alone, and each district needs one unmistakable landmark so the town is navigable without a map.
**Rules that follow:**
- Heights are a hierarchy, not noise: Town Hall > Auction House ≈ Library > Trade > Slums. Nothing in the slums may exceed a trade shop.
- A **parish church** (nave, buttressed tower, spire) stands in the north-east quarter as the one landmark outside the five districts — a town this size needs one, and it breaks the ring of housing. It is *not* a sixth district and owns no streets.
- The Town Hall faces the plaza; the plaza is the hub all four districts touch.
- The library is *adjacent to* the slums but walled off from them — that contrast is the point.
- District identity must survive the art pass. Slum materials stay patched and unpainted; Town Hall gets dressed stone and glass; the Auction House may be the only building with metalwork.
- Names: neutral functional district names only (Town Hall, Trade District, Auction House, The Slums, Library). No proper names until `Docs/DESIGN.md` locks them, and never the inspiring novel's names.

### ADR-015 — Streets and ground profile — Accepted (network and ground profile superseded)
**Partly superseded by `CITY_LAYOUT.md` revision C:** the street hierarchy and carved-road logic stand; the network is `CITY_LAYOUT.md` §6, the terrace profile is dropped (§9, the town is flat at z 0), and the kerb is **45 cm × 12 cm** with a 1.5 m zone, not the 150 cm kerbs below.
**Street hierarchy:** four tree-and-flagstone axes from the gates to the plaza, plus a ring road just inside the wall and short approaches outside each gate. The roads are **carved, not painted**: each is a 40 cm slab faced by 150 cm kerbs, because a flat slab in one material is invisible in greybox and reads as ground clutter. Deletions were required to open them — the trade high street runs through where four shops stood, the south spine through a rank of hovels, the north approach through two houses. Those gaps are the street, not a mistake.
- **North axis** — plaza → Town Hall steps → north gate. This is the ceremonial approach; it must stay the widest clear sightline to the clock tower.
- **West axis** — plaza → west gate, the high street of the Trade District. Shops front it on both sides.
- **South axis** — plaza → south gate, cutting through the Slums. Deliberately the narrowest-feeling route even at the same width, because the buildings flanking it are half height.
- **East axis** — plaza → Auction House courtyard. Short and framed, terminating on the dome.

**Ground profile:** the town sits on a plateau at 800 m elevation with a **stepped** descent west to the quay (five 82 m flights, 690 → 250) and a stepped ascent east to the ridge (six 100 m steps, 900 → 1400). Cubes plus steps, not ramps: primitives cannot be reliably tilt-authored through this toolset, and stepped terraces match the terrace logic of the reference anyway.
**Why:** a town on a plinth reads as a diorama; a town that *descends* to its river reads as a place. The same applies to streets — a network you can see is a network players will use.

### ADR-016 — Massing variety is authored, not incidental — Accepted
**The bug this closes:** every building stood on a hard-coded height inherited from the terrain as it was *when that district was written*. When the plateau rose from 600 to 800, the wall ring and gate towers kept their old base and hung 200 in the air, while the shops — written later against 800 — sat correctly. A blockout must have exactly **one** ground constant per surface, and every mass derives its base from it.

**Variety ranges, per district** (width × depth × height, cm):

| District | Footprint | Height | Roof | Extra |
|---|---|---|---|---|
| Trade shops | 620–1400 × 560–1320 | 820–1600 | cone, flat parapet or ridge, chosen per building | jettied upper storey above 1250 |
| Slum hovels | 420–940 × 380–810 | 300–760 | lean-to or patch slab | yaw ±35°, position jitter ±350 |
| North townhouses | 640–1260 × 620–1180 | 760–1340 | cone or ridge | jetty above 1040 |
| Market stalls | 500–900 × 400–700 | 300–500 | awning slab | varied counter heights |

**Rules:**
- No two adjacent buildings share both footprint and height; heights are drawn from a per-district set, never a single value.
- Variety never breaks the district hierarchy of ADR-014: a slum hovel stays below the tallest trade shop.
- Randomness is seeded (`_seed` in the generator script) so a rebuild is reproducible and a capture is comparable.
- Shape, not ornament, carries the variation for now: footprint, height, roof type, jetty overhang, yaw. Trim, signage and colour belong to the art pass.

---

### ADR-017 — Village first: surroundings stripped until the town is signed off — Superseded
**Superseded by `CITY_LAYOUT.md` revision C (ADR-025):** the river, bridges, stream, waterfall and ridge are back in the plan and built in `LVL_StarterVillage_V3`. Kept below as history.
**Decision (owner):** stop spending effort on the river, terraces, slopes, hill, bridges, docks, boats and trees. The trees, water and surrounding terrain have been removed from `LVL_StarterVillage_V2`. The village itself is the only subject until it is good.
**Consequences:**
- ADR-013 (river town on terraces) and the ground-profile half of ADR-015 are **deferred, not cancelled** — the design for the river remains recorded there for when the village is signed off.
- The plateau slab stays: it is the ground the village stands on, not scenery. Every mass derives its base from it (ADR-016).
- The pre-trim level is preserved outside version control at `Game/Saved/LVL_StarterVillage_V2.backup.umap` (604 KB, includes river, terraces, 48 trees). Do not delete `Game/Saved/` while this is the only copy of that work.
- A settlement still needs an edge: the ring inside the wall was filled with `Town/WallBelt` buildings so the village backs onto its curtain wall instead of trailing off into empty ground.

### ADR-019 — Starting village art direction: painterly late-medieval autumn — Proposed
**What:** the village reads as a grounded-but-painterly late-medieval market town in high autumn — warm ochre plaster over dark oak framing, terracotta roofs, pale dressed stone for civic and church, cool blue sky. Full spec in `ART_DIRECTION.md`; canonical palette in `Tools/Blender/palette.json`.
**Why:** the owner supplied a concept image, and a written spec turns "make it feel like this" into decisions that can be checked per asset. The palette lives in a JSON file rather than prose so textures, kit and lighting all read the same values.
**Consequences:** six material families only (variation from UVs, instance tint and decals); no baked directional light in any texture; red is reserved for banners, awnings and fire; cathedral/town hall stone is the only "clean" material; the ADR-014 district hierarchy survives the art pass and is carried by material condition, not colour-coding.
**Open:** stylisation level, hero-facade exceptions, banner sigil, foliage budget.

### ADR-020 — Procedural-first textures generated from a palette file — Proposed
**What:** `Tools/Blender/generate_textures.py` (numpy only, no add-ons) generates tileable BaseColor/Roughness/Normal/Height for the six material families from `Tools/Blender/palette.json`, at 1024 px over a 2 m tile (512 px/m). Runs headless in Blender or under system Python; output to `Art/Exports/Textures/`.
**Why:** one artist, so styling must be cheap to change: a colour is a JSON edit and a 10-second re-run, and the diff is reviewable text instead of an opaque binary. Seeded from the material name, so sheets are reproducible.
**Trade-off:** procedural surfaces do not tell a story by themselves — hand-painted grime, decals and hero overrides carry that later. Accepted, because a repainted sheet is the expensive path and the sheets need to exist before the kit can be judged.
**Machine note:** Blender on this workstation is the **Steam** build at `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe` (**5.3.0**), not on `PATH` and not in `C:\Program Files\Blender Foundation`. Headless runs use the full path; `AGENTS.md` and `MCP_SETUP.md` should use the same path.

---

## Template
```
### ADR-XXX — Title — Status
Why:
Trade-offs / alternatives:
```
