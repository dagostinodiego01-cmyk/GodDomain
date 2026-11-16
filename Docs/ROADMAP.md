# Roadmap — First Playable Draft

**Goal of this roadmap:** a packaged build in which someone else can walk the starter village, fight two kinds of enemies with two weapons and four skills, and get promoted — with the village carrying the look in `ART_DIRECTION.md`.

Status: **Proposed.** Milestones are ordered by dependency, not by importance. Work runs on three tracks: **code** (M1→M5, then M7 and M8 — start a task only when everything in its *Depends* column is ✅), **tooling** (X, alongside M1) and **art** (M6, on the editor machine, once M6-01 is signed off). A milestone closes when its exit criterion is met.

---

## How to read this

- Every task has an **ID** (`M4-05`), a size, its **dependencies**, and a *done when* that a person can actually check.
- **Size:** `S` ≈ half a session, `M` ≈ one session, `L` ≈ two to three sessions.
- A task is done when it builds, has no new warnings, states its replication behaviour, and — if gameplay — can be verified in the editor. That is the checklist in `AGENTS.md`; it is not repeated per row.
- Anything marked **⛔ ask** needs an owner decision before work starts.
- **Agent** — who should do the task. `A`: a cheap model (e.g. DeepSeek 4.1 Flash) working from its card in `TASK_CARDS.md`. `B`: a strong model (cross-system design, replication and prediction, AI, debugging). `E`: the editor/Blender machine through MCP (assets, levels, captures). `O`: the owner (feel, sign-off, decisions). `A+E`: the C++ is `A`, then an asset or hook-up step on the editor machine. Done rows show `—`.
- A **session** is one agent conversation, from reading the task to a clean build.

**Current state (2026-11-15):** M0, X-01, X-02, M1-01, M1-02 and M1-03 are done, and the greybox city `LVL_StarterVillage_V3` (499 actors) is the live map. Code and editor work happen on a separate machine and may not be pushed yet; if a file a task names is missing here, that is why. What was built is described in the **Done log** at the end.

**Rough total:** ~100 focused sessions. The village (M6) is the largest single block; combat (M1–M5) is the longest critical chain.

---

## Milestones at a glance

| # | Milestone | Why it exists | Exit criterion |
|---|---|---|---|
| **M0** | Foundations | Engine, project, git+LFS, rules and docs | ✅ complete 2026-11-15 |
| **M1** | Combat core | Nothing else matters if hitting things is not fun | A fight against a dummy in a test arena feels right |
| **M2** | First enemy | Proves the whole loop: aggro → attack → damage → death | One brute can chase, hit and be killed |
| **M3** | Weapons | Two weapons that feel different make combat a choice | Sword and axe play differently and swap in-game |
| **M4** | Class & skills | Data-driven progression is the game's spine | Editing a CSV changes the game without recompiling |
| **M5** | Second enemy | Two archetypes make an encounter, not a training dummy | Brute + caster fights are readable and winnable |
| **M6** | Village as a place | The "city draft" — art, light, dressing, navigation | Seven capture views (V1–V7) match the art direction |
| **M7** | Services & loop | Ties the village to progression | New player: spawn → quest → fight → promote → buy |
| **M8** | First playable | Ship the thing to one other person | A packaged build another person plays for 30 min |
| **M9** | Co-op | Only after single-player is fun | Two machines in the village together |
| **X** | Cross-cutting tooling | Makes every other milestone cheaper | Debug commands, smoke test, profiling baseline |

---

## X — Tooling and foundations (do first, in parallel with M1)

| ID | Task | Depended on by | Size | Agent | Done when |
|---|---|---|---|---|---|
| X-01 | ✅ `Core/` skeleton: game mode, game state, player state, player controller, log categories — ADR-022 | everything | S | — | Project builds; a log line appears from the new category |
| X-02 | ✅ Debug cheats in `UGodDomainCheatManager`: `GiveXP`, `SetLevel`, `SetClassTier`, `SpawnEnemy`, `GodMode`, `KillTarget` — ADR-023. `GodMode`/`KillTarget` only bite once M1-05 lands; `SpawnEnemy` spawns a stand-in until M2-01 | M2–M7 testing | M | — | Each command works from the console in PIE |
| X-03 | Smoke test: a commandlet or functional test that loads the village, spawns one enemy, applies damage, asserts death. **Needs** M1-05 and M2-05 | X-04, M2+ | M | B | Runs headless, exits non-zero on failure |
| X-04 | Local check script: build + automation tests + report, one command. Ship it build-and-unit-tests first; add the X-03 smoke step when that exists | every commit | S | A | One command tells you pass/fail |
| X-05 | Profiling baseline: capture `stat unit` / `stat game` in the village on this machine, store the numbers in `Docs/` | M6, M8 | S | E | A documented baseline to regress against |
| X-06 | Data validation: on import, fail loudly if a CSV row references a missing skill, item or class, or has a value outside its declared range | M2-01, M3-01, M4 | M | A | A deliberately broken row is reported with the row id |

---

## M1 — Combat core

**Exit:** you can walk, dodge, swing, take a hit and die against a stationary dummy in `LVL_TestArena`, and it feels like it has weight.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M1-01 | ✅ `AGodDomainCharacter` in `Characters/`: spring arm + camera, `WalkSpeed`/`RunSpeed`/`SprintSpeed`, crouch off; feel sign-off stays with M1-11 — ADR-024 | X-01 | M | — | Third-person movement matches or beats the template's feel |
| M1-02 | ✅ Enhanced Input: Move, Look, Jump, Sprint, Dodge, Light, Heavy, Skill1–4, Interact in `IMC_Default` + `IMC_Combat`; Sprint is a replicated intent — ADR-026 | M1-01 | M | — | No legacy input bindings remain |
| M1-03 | ✅ GAS bootstrap: ASC on the character (Mixed), `UGodDomainAttributeSet` subobject, `InitAbilityActorInfo` on the server (`PossessedBy`) and client (`OnRep_Controller`) — ADR-026 | M1-01 | M | — | Health prints on both sides; `AbilitySystemComponent` valid in `BeginPlay` |
| M1-04 | Attribute set: Health, MaxHealth, Stamina, MaxStamina, AttackPower, Defense, MoveSpeed; clamping + OnRep. Starting values come from data (an init GE or `DT_` row), not the constructor — M1-03's 100/100 moves there | M1-03 | M | A | A GE changes values; they replicate to the client |
| M1-05 | Damage pipeline: `FGodDomainDamageEvent`, one `ApplyDamage` path → `GE_Damage_Basic` + `ExecCalc` (power × multiplier − defense, clamped) | M1-04 | M | B | Every damage source routes through one function; log shows amount and source |
| M1-06 | Death: `State.Dead` tag, death montage, input disabled, respawn timer | M1-05 | S | A+E | Character dies and respawns without a manual reset |
| M1-07 | Dodge: montage, i-frames window, stamina cost, cancels attack recovery | M1-02, M1-04 | M | B+E | Dodging through an attack avoids damage; dodge is cancelled by running out of stamina |
| M1-08 | `LVL_TestArena`: flat floor, four walls, pillars at 4/8/12 m, one training dummy with health and a respawn | M1-01 | S | E | Arena is playable at 180 cm character height |
| M1-09 | Hit feedback: hit-stop (~60 ms), camera shake, target flash, placeholder SFX | M1-05 | M | A+E | A hit is distinguishable from a whiff with eyes closed |
| M1-10 | Health/stamina HUD stub (numbers on screen is enough) | M1-04 | S | A | Values move during a fight |
| M1-11 | **Feel tuning pass** — movement, camera, dodge distance, hit-stop, shake | M1-01…M1-10 | M | O | Owner signs off: "a fight feels good" |

---

## M2 — First enemy

**Exit:** a brute patrols the arena, aggros, closes, attacks, damages you, and dies to your attacks with XP awarded.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M2-01 | `AGodDomainEnemyCharacter` + ASC, `Enemy` tag, health from data: adds `FGodDomainMonsterRow` and `Data/Monsters.csv` (moved here from M4-01) | M1-05, X-06 | M | A | Enemy has authority-owned health that replicates (logged on server and client); the bar itself is M2-04 |
| M2-02 | AI controller + behaviour tree: patrol → aggro (radius) → chase → attack (range) → strafe → leash back to spawn. **No Tick.** | M2-01 | L | B+E | Enemy behaves correctly with the player standing still, running, and leaving range |
| M2-03 | Enemy attack ability: montage, hit window notify, damage GE on the player | M2-02 | M | B+E | Player loses health when hit; missing the window does nothing |
| M2-04 | World-space enemy health bar | M2-01 | S | A | Bar follows, hides at full health, faces camera |
| M2-05 | Enemy death: montage/ragdoll, disable collision, reward hook (XP + item roll) | M2-03 | M | A+E | Death fires exactly one reward event |
| M2-06 | `AGodDomainSpawnPoint`: count, respawn delay, radius, activate on player proximity | M2-05 | M | A | Two spawn points in the arena populate and refill |

---

## M3 — Weapons

**Exit:** sword and axe are visibly, measurably different — speed, reach, damage — and swapping mid-run works.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M3-01 | `FGodDomainWeaponRow` (CSV) + `UGodDomainWeaponData`: id, type, damage multiplier, swing speed, reach, socket, montage set, mesh | M1-05, X-06 | M | A | Two rows load; a bad row is rejected by X-06 |
| M3-02 | Weapon component: attach to socket on both server and client, replicate equipped weapon id | M3-01 | M | B | Another client sees the right weapon in the right hand |
| M3-03 | Weapon-driven attack: montage rate from weapon speed, hit sweep from socket with weapon reach, damage × weapon multiplier | M3-02 | L | B | Same ability, two weapons, different numbers and different timing |
| M3-04 | Two weapons modelled (greybox is fine): `SM_Weapon_Sword_01` (1H, fast, 180 cm reach), `SM_Weapon_Axe_2H_01` (2H, slow, 240 cm reach) | M3-01 | M | E | Both import at correct size; pivots at grip |
| M3-05 | Light chain: two-hit combo per weapon + heavy finisher, input buffer window, cancels | M3-03 | L | B+E | Combo reads: light → light → heavy; input feels responsive, not mashed |
| M3-06 | Equip/swap: hotkey, animation set switch, HUD slot | M3-02 | M | A+E | Swapping mid-fight keeps state consistent |

---

## M4 — Class and skills (data-driven)

**Exit:** the class, its tiers, four skills and the XP curve all live in data; changing a number in CSV changes the game without a recompile.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M4-01 | Row structs + CSVs for the rest: `XPCurve.csv`, `ClassTiers.csv`, `Skills.csv`, `Items.csv` in `Data/` (`Monsters.csv` comes from M2-01, `Weapons.csv` from M3-01) | M3-01, X-06 | M | A | Tables import; structs match columns |
| M4-02 | `UClassDefinition` data asset: id, display name, role, weapon types allowed, starting skills, promotion nodes | M4-01 | M | A | Asset edited in-editor references abilities by soft pointer |
| M4-03 | `UGodDomainClassSubsystem`: registry of class definitions, resolve by id, assign to `PlayerState`, apply tier-0 attributes | M4-02 | M | A | Two definitions can coexist without code changes |
| M4-04 | XP and levels: grant from kills (quest grants arrive with M7-03), curve from CSV, level-up GE, attribute growth per level | M4-01, M2-05 | M | A | Reaching level 5 changes stats exactly as the curve says |
| M4-05 | Skill base class `UGodDomainGameplayAbility`: cost/cooldown GEs, activation blocking tags, `Authority: server` comment | M1-03 | M | B | All skills inherit it; no duplicated cost logic |
| M4-06 | **Skill 1 — Light Strike**: free, fast, no cooldown, the default attack | M3-03, M4-05 | S | A | Holds up as the bread-and-butter attack |
| M4-07 | **Skill 2 — Cleave**: cone AoE, stamina cost, 6 s cooldown, hits up to 3 targets | M4-05 | M | A | Hits exactly the targets in front, inside the cone |
| M4-08 | **Skill 3 — Charge**: gap closer, 10 s cooldown, damage on arrival, breaks enemy wind-up | M4-05 | M | B | Distance covered matches the animation; can be used to interrupt a telegraph |
| M4-09 | **Skill 4 — Guard**: 2 s stance, damage reduction GE, stamina drain, slows movement | M4-05 | M | A | Reduces damage by the data value and no more |
| M4-10 | Two passives applied on unlock (e.g. stamina regen, +damage vs staggered) | M4-05 | S | A | Visible in the attribute panel / logs |
| M4-11 | Skill bar UI: 4 slots, cooldown sweep, cost-shortage state | M4-07…M4-09 | M | A+E | Cooldowns read at a glance |
| M4-12 | Promotion: tier 0 → tier 1 in data (required level + quest id), stat reset/bump, skill set change, visual accent | M4-02, M4-04 | M | B | Promotion via debug command first, then via quest in M7 |
| M4-13 | **Balance pass 1**: skill damage/cost/cooldown vs enemy health in CSV only | M4-06…M4-12 | M | O | Four skills are all worth using; none trivialises a fight |

---

## M5 — Second enemy and encounters

**Exit:** two archetypes that demand different responses, placed in two tuned encounters.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M5-01 | Ranged caster archetype: projectile ability, keep-distance behaviour, longer wind-up | M2-02 | L | B+E | Caster retreats when closed on, telegraphs before firing |
| M5-02 | Rank variants via data: normal/elite multipliers, tint, name suffix | M2-01 | S | A | Elite reads as elite at 20 m without a label |
| M5-03 | Two encounters at the village edge: 3 brutes; 2 casters + 1 brute. Patrol routes, leash, reset | M2-06, M5-01 | M | E | Fights are winnable at tier 0 with skill, brutal if you stand still |
| M5-04 | Readability pass: telegraph decal/VFX colours, wind-up audio placeholder, hit reaction direction | M5-03 | M | E | You can tell what will hit you before it does |
| M5-05 | **Balance pass 2**: time-to-kill, incoming damage, stamina economy | M5-03 | M | O | A normal fight lasts 20–40 s; dying feels earned |

---

## M6 — Village as a place (the city draft)

Maps to `ART_PIPELINE.md` phases P1–P5. P4 landscape follows P1–P3 (ADR-017's deferral is superseded — V3 has the river and ridge). The plan is frozen as **`CITY_LAYOUT.md` revision C** (ADR-025): 420 × 330 m map, **300 × 200 m walled town**, slums outside the south wall, **300 street buildings**, seven capture views. Phase A of that document (the greybox rebuild) comes before M6-03.

**Phase A done 2026-11-15:** `LVL_StarterVillage_V3` exists — **499 blockout actors** generated from the CSV by `Tools/Editor/build_level_v3.py` through the editor's MCP server, in folders under `GD/Greybox`: **300 individual buildings** (one per `count`, in rows, 3.5–16 m), ground cut along the river in 14 slices, 28 wall runs cut at every gate, 13 towers, 19 gate piers/lintels, 27 street pads clipped at both water crossings, 13 landmarks, 2 bridges with decks/steps/parapets/piers, 6 plazas, 25 water pieces, 13 props, and a two-terrace ridge with the waterfall. Eight material instances on duplicated meshes give ground, water, stone, plaster, slum and paving their own colour. Template floor removed, PlayerStart on the south bank at `(0,-160)` facing north.

The first pass was **not** good enough and was rebuilt after a walk-through: block rows were single boxes with their middles cut out (unreadable, unusable for model swapping), the gates read as scattered blocks, the river and bridges were invisible because the water was a 3 cm marker inside a solid slab, and the ridge was one flat 80 x 85 m slab. Each of those is now geometry, not a note.

**Audited against the plan (2026-11-15):** `Tools/Editor/compare_level_to_plan.py` measures every greybox actor and compares it with the CSV — **118 checks, 118 pass, 0 flagged**. The block array is measured as an array: 37 blocks holding exactly the CSV's **300** buildings (the builder used to round per row and came out five short), every plot inside a row identical to 1 cm, party gap 0.40 m, no block on a road or above the ground, and every block's footprint and frontage within 0.3 m of its plan rect. The SVG carries a numbered pin per gate, bridge, district and landmark with the measured value in a legend band, so no callout sits on the geometry. Gate passages 8/6/6/8/4/6 m clear; river 16.0 m wide, surface −4.55 at both crossings; bridges 16 × 28 and 26 × 10 with +1.2 m decks, six risers each and two piers; roads 5–10 m as specified (Ridge Road traced, it is diagonal); district extents within 0.2 m; cathedral west front 38.0 m, towers 44 m, flèche 58 m; auction drum Ø28.0 at (80, 40). Report: `Docs/Layout/Level_vs_Plan.md`, overlay: `Docs/Layout/Level_vs_Plan.svg`. The one deliberate deviation — the stream at −1.0 instead of +2.0 — is recorded with its reason in `CITY_LAYOUT.md` §13.

**V3 is the live game map (2026-11-15):** `DefaultEngine.ini` points `GameDefaultMap` and `EditorStartupMap` at it. Boot proven from project defaults: Play on V3 spawns the character on the south bank, `AGodDomainGameMode` logs a clean match start, all 499 actors load, no errors or warnings in the log, and a sightline trace from the spawn reaches the square through the gate without a hit. Awaiting the owner's walk-test and the revision-C sign-off before M6-02.

**Exit:** the seven capture views V1–V7 in `CITY_LAYOUT.md` §11 (gate arrival, square centre, High Street, auction approach, slum lane, library court, parvis look-back) match `ART_DIRECTION.md`, and no grey primitive is visible inside the walls.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M6-01 | **Layout freeze v3** — sign off `CITY_LAYOUT.md` revision C: a **300 × 200 m walled town** on a 420 × 330 m map (wall, gates, four axes, square, districts, landmarks, levels, anchors, **300 buildings**) **plus back alleys** behind the block rows in every district (owner decision 2026-11-16, `CITY_LAYOUT.md` §10), and rebuild the greybox from `Data/Layout/city_layout.csv` | ⛔ ask | L | O+E | Revision C is signed off and `LVL_StarterVillage_V3` matches the plan; further layout changes need a decision |
| M6-02 | Scale pass: 320 cm storeys, 200 cm bays, 100×210 doors, eye height 165 cm | M6-01 | M | E | Character walks under every archway; nothing feels toy-sized |
| M6-03 | Ground kit placed: `SM_Ground_Plaza` (+ `_Worn`), `SM_Road_Strip`, `SM_Kerb_Straight/Corner`, `SM_Gutter_Run`, `SM_Step_Rise`, `SM_Grass_Patch/Verge` replacing slabs and kerb cubes; `T_Cobble` kept for courtyards and back lanes | M6-01; P0 sheets + `GroundKit.blend` (editor machine) | M | E | No grey slab visible at player height |
| M6-04 | Facade kit P1 — trade district first: wall bays, corner posts, jetty bands, braces, doors, windows, roofs, chimneys, eaves | M6-02 | L | E | One trade row rebuilt with kit only; reads as half-timbered |
| M6-05 | Facade kit applied to town hall, north housing, wall belt | M6-04 | L | E | Districts still distinguish by height/density before colour |
| M6-06 | Plaza dressing P2: fountain rebuild, well, benches, planters, stalls with awnings, barrels, crates, carts, signboards (no text) | M6-03 | L | E | Plaza has a reason to stand in it; empty square is gone |
| M6-07 | Civic kit P3: town hall facade, colonnade, gate towers with arches and caps, banner poles with geometric sigil | M6-04 | L | E | Landmarks read as the height ladder's top |
| M6-08 | Slums pass: patched plaster, smoked timber, lean-tos, laundry lines, scavenged boards, tighter alleys | M6-04 | M | E | The only district whose *front* materials are worn rather than old (back alleys are M6-15) |
| M6-09 | Library and cathedral detail: buttresses, tall windows, the rose window on the west front, pinnacles, courtyard wall | M6-07 | M | E | The stone buildings are the only cold-pale silhouettes; the flèche is the only thing above 40 m |
| M6-10 | Lighting: warm sun at 25–35°, sky, distance haze toward the ridge (no street fog), exposure, lit windows, lanterns, forge glow | M6-03 | M | E | Warm/cool split reads; shadows are blue-grey, never black |
| M6-11 | Decals P5: leaf litter, cobble cracks, moss at kerbs, soot, standing water | M6-10 | M | E | Surfaces stop being uniform at 2 m |
| M6-12 | Navigation and collision: navmesh through streets/plaza/alleys, `UCX_` collision on everything walkable | M6-05 | M | E | Enemies path from gate to plaza without getting stuck |
| M6-13 | Sightline verification: the seven captures V1–V7 from `CITY_LAYOUT.md` §11, each checked against its *fails if* column | M6-10 | S | O | Owner signs off each view |
| M6-14 | Village perf pass: HISM for repeated props, LODs on kit, lightmap density, 60 fps at 1080p on this machine | M6-12, M6-13 | M | E+B | X-05 baseline beaten or matched inside the walls |
| M6-15 | Back alleys: dress the alley rows from M6-01 — smoked timber, stained and patched plaster, puddled setts, refuse, few lanterns, deep shadow under jetties; front streets stay warm (`ART_DIRECTION.md`) | M6-04, M6-11 | M | E | Turning off any front street into an alley is a visible drop in light and care |

---

## M7 — Services, quest and save (the loop)

M7 is built and tested in `LVL_TestArena`; only placing the board, trainer and vendor in the village waits for M6-12.

**Exit:** a new player spawns, accepts the trial at the board, kills five enemies, returns, is promoted by the trainer, and buys a weapon from the vendor.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M7-01 | Interaction system: `IGodDomainInteractable`, prompt, server-validated interaction, range check | M1-02 | M | B | No client-side authority over interactions |
| M7-02 | NPC base + idle behaviour (look-at, idle anims, day schedule later) | M1-01 | M | A+E | NPCs react without Tick |
| M7-03 | Quest board and quest data: two quests (clear the outskirts; the promotion trial), objectives, tracker, completion | M7-01 | L | B | Objectives update from kills; abandoning works |
| M7-04 | Class trainer: dialogue stub, promotion gate (level + trial quest), applies tier 1 | M4-12, M7-03 | M | A | Promotion cannot be triggered early via the trainer |
| M7-05 | Vendor: buy/sell from `Items.csv`, copper currency, minimal inventory list | M4-01, M3-06 | L | B | Buying the axe deducts the right amount and equips |
| M7-06 | HUD completion: health, stamina, skills, XP bar, quest tracker, interaction prompt | M4-11 | M | A+E | Everything readable at 1080p without opening a menu |
| M7-07 | Save/load: `USaveGame` for position, level, XP, class/tier, inventory, quest state; autosave on exit and rest | M7-05 | M | B | Reloading the build restores the exact state |
| M7-08 | Audio MVP: footsteps, swing, hit, enemy death, ambience loop, UI clicks | M1-09 | M | E | Combat is not silent; no music dependency |

---

## M8 — First playable draft

**Exit:** a packaged build that another person installs and plays for 20–30 minutes without a crash, and a list of known issues.

| ID | Task | Depends | Size | Agent | Done when |
|---|---|---|---|---|---|
| M8-01 | **Balance pass 3** across XP, damage, enemy health, prices | M7-08 | M | O | 20–30 minute path to promotion, measured not guessed |
| M8-02 | Bug bash: crashes, log spam, `LogTemp` leftovers, Tick audits | M7-08 | L | A | Zero `LogTemp` in committed code; no Tick in gameplay classes |
| M8-03 | Packaging: Shipping config, startup map, window settings, content cooking | M8-02 | M | E | Packaged build launches on a machine without the editor |
| M8-04 | Perf validation in the packaged build | M8-03 | S | E | 60 fps target holds; numbers recorded |
| M8-05 | Playtest kit: 5-minute brief, feedback form, capture set | M8-03 | S | O | One external playtester completes the loop |
| M8-06 | Tag `v0.1-first-draft` + release notes with known issues | M8-05 | S | A | Tag pushed; notes list what is deliberately unfinished |

---

## M9 — Co-op (deferred until M8 is signed off)

Every M9 task depends on M8-06.

| ID | Task | Size | Agent | Done when |
|---|---|---|---|---|
| M9-01 | Replication audit of every gameplay class: properties, RPCs, prediction | M | B | A written audit with each class marked server/client/both |
| M9-02 | Listen-server sessions for 2–8 players; ability prediction review | L | B | Two clients fight the same enemy with consistent health |
| M9-03 | Two-machine test, including a dropped connection | M | O | Session recovers or fails cleanly |

---

## Assumptions this roadmap makes — ⛔ owner sign-off needed

These are choices I made so the list could be concrete. Change any of them and the affected tasks shift, not the structure.

| # | Assumption | Affects |
|---|---|---|
| 1 | **First class is melee**, one-handed and two-handed capable | M3, M4 |
| 2 | **Two weapons:** fast 1H sword (180 cm) and slow 2H axe (240 cm) | M3, M7-05 |
| 3 | **Four skills + two passives:** Light Strike, Cleave, Charge, Guard | M4 |
| 4 | **Two enemies:** melee brute and ranged caster, each with a normal and elite variant | M2, M5 |
| 5 | **Promotion at tier 0 cap**, gated by one trial quest | M4-12, M7-04 |
| 6 | **Session length target: 20–30 minutes** to promotion | M8-01 |
| 7 | **Audio is placeholder-quality**; no music dependency | M7-08 |
| 8 | **Single class only** — the data model supports more, but no second class is built | all |

## Scope guardrails

Not in this roadmap, deliberately: crafting, player economy beyond one vendor, housing, mounts, city building, dedicated servers, persistence beyond one save slot, localisation, character customisation, a second class or zone, and any text on signage (IP rule).

## Critical path

```
X-01 → M1-01 → M1-03 → M1-04 → M1-05 → M1-11
                    ↓
            M2-01 → M2-02 → M2-03 → M2-05
                    ↓
            M3-01 → M3-03 → M3-05
                    ↓
            M4-01 → M4-05 → M4-06…09 → M4-13
                    ↓
            M5-01 → M5-03 → M5-05   →   M6-* (art, parallel once M6-01 frozen)
                    ↓
            M7-03 → M7-04 ─┐
            M7-05 ──────────┴→ M7-07 → M8-*
```

Art (M6) can run in parallel from M2 onwards once M6-01 is frozen — it is the only track that does not block code.

## Next ten tasks

In dependency order. The letter is the Agent column; `A` tasks get a card in `TASK_CARDS.md` once their dependencies are ✅ (M1-04, X-04 and M1-10 have one now).

1. `M1-04` Attribute set — A
2. `M1-08` Test arena — E (editor machine; can start now, in parallel)
3. `X-04` Local check script, build + unit tests — A (can start now)
4. `M1-05` Damage pipeline — B
5. `M1-10` Health/stamina HUD stub — A (needs M1-04)
6. `M1-06` Death and respawn — A+E
7. `M1-09` Hit feedback — A+E
8. `M1-07` Dodge — B+E
9. `M1-11` Feel tuning pass — O (needs M1-01…M1-10, so it is last)
10. `M2-01` Enemy character with health — A

## Open questions blocking work

1. **Class identity and name** — needed before `UClassDefinition` is authored (`DESIGN.md` still says TBD).
2. **Weapon set confirm** — assumption 2 above.
3. **Promotion gate** — level threshold and whether the trial quest is combat-only.
4. **Layout freeze** — `CITY_LAYOUT.md` revision C is the freeze candidate (300 × 200 m walled town on a 420 × 330 m map, 300 buildings); M6-01 must be signed off before any kit is imported into the village.
5. **Art direction sign-off** — `ART_DIRECTION.md` is still *Proposed* (ADR-019); M6 is built on it.
6. **Plot-width infill** — 10 cm closure panels for plots that are not whole 200 cm bays, proposed in `Art/Concept/CITY_ART_STYLE.md`; needed before M6-04.

---

## Done log

History moved out of the task tables so they stay short.

**2026-11-15:** M0 complete. Greybox city committed (`LVL_StarterVillage_V3`, 499 actors, built from `CITY_LAYOUT.md` revision C; river, bridges and ridge included). Editor/Blender work and some code are done on a separate machine and may not be pushed yet — the completions below describe that machine's state. Material sheets generated (`Tools/Blender/generate_textures.py`). **X-01 complete:** `Core/` exists with the log categories (`LogGodDomain`, `LogGodDomainCombat`) and the game mode / game state / player state / player controller skeleton, wired from the game mode constructor. **X-02 complete:** `UGodDomainCheatManager` provides `GiveXP`, `SetLevel`, `SetClassTier`, `GodMode`, `KillTarget` and `SpawnEnemy` in PIE, all six exercised in one headless console run; progression state is replicated on `AGodDomainPlayerState`. `SpawnEnemy` resolves roster entries first, then the game mode's `DebugDefaultEnemyClass` (default: the hero pawn), so it spawns a real actor today — **notes for M2:** the spawned stand-in is not an enemy, and `GodMode`/`KillTarget` still wait on the damage path (M1-05/M2-05). **M1-01 complete:** `AGodDomainCharacter` lives in `Source/GodDomain/Characters/` with the movement tuning (`WalkSpeed`, `RunSpeed`, `SprintSpeed`), the spring-arm camera and crouch disabled; PIE on `Lvl_ThirdPerson` logs the applied values on `BP_ThirdPersonCharacter_C_0` and the pawn moves under input (ADR-024). **M1-02 complete:** all twelve M1 actions are bound (Move, Look, Jump, Sprint, Dodge, Light, Heavy, Skill1–4, Interact), the combat ones through a project `IMC_Combat` alongside the template's `IMC_Default` — the nine combat actions and the context are real assets (`Game/Content/Input/…`, built by `Tools/Unreal/create_input_assets.py` and assigned on `BP_ThirdPersonCharacter`), with the C++ subobject set kept as the no-content fallback. Sprint is a replicated intent: a dedicated server plus a client logged the client's prediction, the server's value 28 ms later and the client's RepNotify 4 ms after that, at 700 on and 500 off on both sides; every press was driven in PIE on that asset-backed context and logged (ADR-026). **M1-03 complete:** `Abilities/` now holds `UGodDomainAttributeSet` (health 100/100), the `UAbilitySystemComponent` on the pawn initialises on both sides — a dedicated server plus a connecting client logged `GAS: ability system ready on the server` and `… on the client`, each with `health 100 / 100` (ADR-026). The enemy-id roster type exists in `Data/` and stays unassigned until M2-01 provides a real enemy class. `Combat/`, `Classes/` etc. are still empty.

Original task rows as completed:

- **X-01** ✅ Create `Core/` skeleton: `GodDomainGameMode`, `GameState`, `PlayerState`, `PlayerController`, `DECLARE_LOG_CATEGORY_EXTERN(LogGodDomain…)` — done 2026-11-15, see ADR-022
- **X-02** ✅ Debug cheat commands: give XP, set level, set class tier, spawn enemy by id, toggle god mode, kill target — done 2026-11-15; all six proven from the console (`SpawnEnemy` spawns the game mode's `DebugDefaultEnemyClass`, currently the hero pawn, because no enemy class exists yet), see ADR-023
- **M1-01** ✅ `AGodDomainCharacter` deriving `ACharacter`: spring arm + camera, walk/run speeds, air control, crouch off. Implementation in `Game/Source/GodDomain/Characters/GodDomainCharacter.*`: `WalkSpeed` 200 / `RunSpeed` 500 applied in `PostInitializeComponents()`, crouch off, 400 camera arm with lag, feel sign-off stays with M1-11 — done 2026-11-15, see ADR-024
- **M1-02** ✅ Enhanced Input actions: Move, Look, Sprint, Dodge, Light, Heavy, Skill1–4, Interact; one IMC per context. Locomotion and camera stay in the template's `IMC_Default`; the nine new actions are `IA_*` assets mapped in `IMC_Combat`, both created by `Tools/Unreal/create_input_assets.py` and assigned on `BP_ThirdPersonCharacter`, with every action still an `EditDefaultsOnly` `UInputAction` and every key an `EditDefaultsOnly` `FKey` and a code subobject set as fallback. Sprint is a replicated intent, not a local speed write: the client predicts from its own intent, the server owns the flag, and the RepNotify was observed on the client in a two-process session — done 2026-11-15, see ADR-026
- **M1-03** ✅ GAS bootstrap: `UAbilitySystemComponent` on the character (Mixed replication), `UGodDomainAttributeSet` registered as a subobject, `InitAbilityActorInfo(this, this)` on the server in `PossessedBy()` and on the client in `OnRep_Controller()` — done 2026-11-15, see ADR-026
