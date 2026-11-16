# Starter city — visual art bible

**Review concept; not an accepted ADR.** 16 November 2026. Open `index.html` in a browser. These are hand-authored text/vector concepts, not engine captures or imported assets. No files outside this concept folder changed.

## Basis and precedence

Required sources read: both AGENTS files; DESIGN, CODING_STANDARDS, ARCHITECTURE, ART_DIRECTION, ART_PIPELINE, CITY_LAYOUT, DECISIONS, Level_vs_Plan; the complete parsed CityPlan.svg and its identical embedded CityPlan.html; palette.json; all five Level_*_V3.png frames. ART_DIRECTION, ART_PIPELINE and CITY_LAYOUT were re-read after the owner's corrections. **CITY_LAYOUT governs all layout, scale and counts.** The CSV and reference PNGs are on another machine: use the local CityPlan and written layout, not invented reference details or a claim of CSV validation.

DESIGN contains no settled proper names. All labels below are functional architectural types under ADR-012/014, not new lore. No named settlement, deity, faction or character is invented. Cathedral describes architecture, not a religion; the draped statue is an anonymous scale study.

**V3 is current and includes the surroundings.** River, both bridges, stream, pool, waterfall and ridge belong in this concept. ADR-017's stripped surroundings are superseded. Landscape modelling P4 still follows P1–P3, but is not deferred out of scope. No separate parish church: its role is the cathedral cloister/chapter house. One flèche at58 m. The town is flat inside its walls.

Overview block bands/counts use the measured table and governing layout: **37 blocks /300 street buildings**, split35 Civic,158 Trade,32 Auction,61 Slums,14 Library. The illustration preserves their positions/counts and the major landmark coordinates. Individual actor widths are often not200 cm multiples: catalogue presets are modular **type examples**, not a claim that every600 cm house fits every actor. Preserve row boundaries, count, streets and gates. Proposed10 cm-grid end closures fill non-bay fronts; never non-uniformly scale doors/windows/beam thickness. A whole-bay-only regrouping would need separate layout approval.

Screenshots show roofless regular arrays, channel cuts and broad bridge decks; placement evidence, not a final material judgement. Level_Top_V3 is south-up as documented, not a north-up relocation guide. The overview has one axonometric projection derived from north-up plan coordinates. Muted district overlays are diagram annotation; **no in-world district paint coding**. The gate skyline is a composed elevation with distant landmark tops intentionally revealed, not an accurate V1 optical reconstruction. River/stream context appears in the inset and flank views because water is not visible on-axis behind the bridge deck.

## Style pillars

1. **Grounded painterliness:** believable180 cm people and100×210 doors; simple chunky planes, subtle broad material variation, no toy proportions or photoreal scratch noise.
2. **Dense useful edges:** attached frontages,40 cm front-only jetties, shadowed eaves, offset chimneys. Every open gap is a street, alley, yard or court. Never decorate the ceremonial axis into an obstacle.
3. **One upward reward:** slums3.5–7 m; trade9–16; gates15–18; library tower30; auction lantern34; Town Hall clock36; cathedral towers44/flèche58. Gothic pointed tracery, pinnacles and rose belong only to cathedral.
4. **Two-material rhythm:** ochre/cream against dark oak, stone against old red tile, roof sea against cold sky. Earthy terracotta is muted, not saturated crimson. Vivid red/orange is a small accent at awnings, banners, forge and autumn leaves.
5. **Warm lived-in morning:** warm low sun at30° elevation, upper-left in compositions, strong cool sky fill; deep reveals but not black shadows. Long cast shadows, no street fog, distant ridge haze only.

### Shape and material language

Domestic ridges parallel streets except turned corner gables. Target roof pitch50°, tower caps60°. Eaves40 cm, framing20×20, wall30, ordinary storeys320/slums280. Deep90×140 windows with small leaded panes;100×210 square domestic doors and round civic doors. Town Hall: broad colonnade and clock, no second Gothic spire. Auction: circular colonnaded drum, broad metal dome and small lantern. Library: plain structural buttresses, tall round windows and square pyramid-capped tower, not pointed Gothic tracery. Cathedral:38 m west front,52 m transept, two44 m towers and58 m crossing flèche. Plain cloister stays in the same stone, without a rival spire.

Six families only: warm/cream plaster, oak, roof tile, cobble, dressed stone. Existing generated textures at1024 px/2 m =512 px/m; existing2048 hero overrides only cathedral stone and plaza cobble. Plaster roughness0.85–0.86, oak0.70, tile0.62, cobble0.80, stone0.78, shared cloth0.85–0.90 and iron0.50. Variation through UV choice, tint and restrained decals, not per-building textures. Wet polish only by damp ground, soot only by smithy, moss by wet bases. SVG light/shadow planes are illustration shading: **never bake those into base colour**.

### Palette by district (canonical palette.json swatch keys)

| District | Main surfaces | Roof / shadow | Small accents |
|---|---|---|---|
| Cathedral & Town Hall | `plaster_cream`, `stone_dressed` | `roof_tile_old`, `timber_oak`, `cobble` | `banner_red`, `banner_gold`, `glass_lit` |
| Trade District | `plaster_warm`, occasional `plaster_cream` | `roof_tile`, `roof_tile_old`, `timber_oak` | `canvas_cream`, `canvas_red`, `glass_lit` forge |
| Auction House | `plaster_cream`, restrained `stone_dressed` | `roof_tile_old`, `timber_oak`, `iron` dome | `banner_gold` emblem; polished metal only here |
| The Slums | patched `plaster_warm`/`plaster_cream` | `roof_tile_old`, `timber_smoked` | `kerb_moss`, `canvas_cream` laundry; no awnings |
| Library | `plaster_cream`, weathered `stone_dressed` plinth | `roof_tile_old`, `timber_oak` | `glass_lit`, `kerb_moss` |

Environment: `sky` for sky/illustrative water and cool fill, `sun` for illumination, neither a wall paint. Foliage: `foliage_rust`, `foliage_amber`, `foliage_deep`. Ground:`cobble`; edges:`kerb_moss`. Canonical material names:`T_Plaster_Warm`, `T_Plaster_Cream`, `T_Timber_Oak`, `T_Roof_Tile`, `T_Cobble`, `T_Stone_Dressed`. No new colours proposed. Neutral diamond/chevron banners and blank sign silhouettes; captions are review labels, not in-world lettering.

## District studies

### 01 — Cathedral & Town Hall / Civic

North precinct X−76…44/Y30…96 zoning; measured civic row bands also extend west. Five blocks/35 houses. Public confidence, clean ceremonial fronts and quiet service backs. Cream infill with dressed-stone podiums; cloister/cathedral same pale stone, old dark tile above, carved oak on houses. Rows8–14 m, nave26, Town Hall body15/clock36, cathedral44/58. Continuous precinct edges around open cloister/court, not a monumental park of isolated buildings.

Signature: cathedral aligned with fountain, subordinate Town Hall west. Props: geometric banners, lamps, carved brackets, steps; trainer at(−56,30), board at(16,18), simple cemetery markers tucked away. From gate: pale west front on the axis, clock to left. From river: the full wall/roof ladder supports the cathedral, not a cathedral placed directly on the bank. Keep20 m ceremonial corridor and12 m square cross clear; ten17 cm parvis risers,30 cm treads, +1.7 m podium.

### 02 — Trade District

West third/south L-band,16 blocks/158 buildings. Busy compressed commerce. Ochre infill, dark oak, mixed-age clay tile and shallow stone bases; two/three storeys9–16 m, jetties, turned corner gables, a few dormers. Height/footprint variation, no identical adjacent pairs. Shops face High Street. Inn wider preset replaces a suitable existing corner plot; smithy remains at forge anchor(−122,−44), not in square.

Signature: High Street's shifting roof/eave/awning line leads toward Town Hall. Abstract signs, counters, barrels, sacks, cart pockets, restrained window boxes. Smithy black hood/stone stack/small amber opening is the sole visible fire inside town. Gate approach: taller layers behind low slums, spine open. River: southern trade rear roofs/chimneys above wall, no invented continuous quay. Leave1.5 m clear pedestrian route around parked carts; eaves/awnings never force player into carriageway.

### 03 — Auction House

X44…150/Y−20…96,3 blocks/32 buildings,56×58 m forecourt. Controlled wealth: busy street outside, quiet walled close inside. Cream, restrained dressed stone, clean dark oak, old-tile domestic hips8–16 m. Ø28 m rotunda,30 m dome/34 m lantern target; broad lead-like `iron`/`roof_tile_old` dome, never gold or a needle.

Signature: dome framed by Forecourt Gate measured at(70,6); entrance anchor(70,16) is distinct.12×10×9 strongroom south-east with narrow weighty door. Iron rails, paired lanterns and sealed crates, no lettering/faction claims. Arrival sees a low broad dome to right, not a second cathedral. River: behind south wall/roof layers; stream bridge: dome signals inland route. Preserve quiet court and clear gate mouth.

### 04 — The Slums

Outside south wall X−124…106/Y−126…−100,12 blocks/61 houses. Repaired, constrained, inhabited; not romantic dereliction. Smoked oak, patched cream over ochre, rough stone bases, old tile/plank repairs.3.5–7 m,280 cm storeys, asymmetrical low lean-tos; up to±10° yaw only where measured boundaries/clearance allow. Worn materials here and in back alleys (below); front facades elsewhere are old but maintained. No retail awnings.

Signature:10 m wall above7 m roofs, river behind viewer. Laundry, buckets, boards, wood stacks without flames, sparse moss/planters. Preserve4 m lane/3 m alleys; props do not encroach Mill Bank encounter(−72,−126). Arrival crosses this suburb before city gate. River read is low backs/north floodplain; working watermill west. **No docks** (owner decision 2026-11-16).

### Back alleys — every district

Owner decision 2026-11-16: the town has back alleys behind its block rows in **every** district, not just the slums — the rear-yard lanes of `CITY_LAYOUT.md` §10. They are the deliberate opposite of the front streets: narrow, dark and run-down. Smoked oak (`timber_smoked`), stained and patched plaster, ragged worn setts with standing water, refuse, broken crates, slop gutters, few or no lanterns, deep shadow under jetties and overhanging upper storeys, `kerb_moss` creeping up wall bases. Front streets stay warm and kept; turning off one into an alley should feel like a drop in light and care. From above they read as dark slots between the roof rows. Worn materials are therefore allowed in the slums **and** in back alleys; front facades elsewhere stay old but maintained.

### 05 — Library

X94…150/Y−96…−20,1 block/14 houses. Old, apart, scholarly quiet. Cream, weathered stone plinth, plain structural buttresses, dark oak, old tile. Round tall windows, no rose/tracery. Rows5–12 m; nave21; SW square tower30 with pyramid cap. Plain precinct wall alongX96; Library Gate(94,−58).

Signature: long north–south roof behind quiet close and one square tower. Bench, planter, shuttered service windows, modest lamp; books inside, no decorative outdoor piles. Gate approach: right-hand silhouette behind southern trade. River: tower above precinct/postern, not a spired second church. From V6(140,−64), buttresses/deep round windows prevent a barn read. Court stays free of stalls.

## Building catalogue — scale convention

**G=10 cm setout unit; B=200 cm bay=20 G.** Fractional B values are deliberate. H is overall silhouette above local base, not a storey multiple. Structural footprint excludes40 cm front eave/jetty allowance; verify clearance independently. Appendages (wheel/sails) are separate. Cathedral uses52×58 m bounding cross-plan, not a solid rectangular hall. West/East Gate front is their1000 cm Y dimension; Library Gate front800. Bridges are drawn along the span; H is river/cut bed to parapet, not above deck.

Each preset is a type example. Narrow plots need the proposed bay+closure assembly, never a resized door. Inn/smithy count inside158 Trade, canonry/auction/scholarly houses inside their existing district budgets; chapter house uses cathedral precinct, final site review, no sixth district. The sheet illustrates one variant per type; variant budgets do not add placed buildings.

| # | Type | District | Footprint B (G) | Footprint cm | H B / G / cm | Variants | Modular assembly | Roof / material |
|---|---|---|---|---|---|---|---|---|
| 1 | Row house | Trade | 3×4 B (60×80 G) | 600×800 | 5.6 B /112 G /1120 | 4 | Facade / jetty / gable / chimney | Clay tile / ochre and oak |
| 2 | Shop | Trade | 3×3 B (60×60 G) | 600×600 | 5 B /100 G /1000 | 4 | Facade / counter / awning / sign / hip | Clay tile / ochre and oak |
| 3 | Inn | Trade | 5×4 B (100×80 G) | 1000×800 | 7.2 B /144 G /1440 | 2 | Facade / jetty / dormer / balcony / gable | Clay tile / ochre and oak |
| 4 | Smithy | Trade | 3×4 B (60×80 G) | 600×800 | 5 B /100 G /1000 | 2 | Planked bays / forge hood / chimney / lean-to | Clay tile / ochre and oak |
| 5 | Slum house | The Slums | 2×2 B (40×40 G) | 400×400 | 2.6 B /52 G /520 | 4 | 280 cm bays / patch panel / lean-to / chimney | Old tile / smoked oak, patched plaster |
| 6 | Canonry house | Civic | 3×3 B (60×60 G) | 600×600 | 5 B /100 G /1000 | 2 | Cream bays / jetty / old tile / chimney | Old tile / cream and stone |
| 7 | Auction townhouse | Auction House | 3×3 B (60×60 G) | 600×600 | 6.4 B /128 G /1280 | 3 | Cream bays / shop door / hip / chimney | Clay tile / ochre and oak |
| 8 | Library row house | Library | 3×4 B (60×80 G) | 600×800 | 5 B /100 G /1000 | 2 | Cream bays / shutter / old tile / chimney | Old tile / cream and stone |
| 9 | Town Hall | Civic | 15×13 B (300×260 G) | 3000×2600 | 18 B /360 G /3600 | 1 | Body 1500 / clock tower 800 square / colonnade / hip | Old tile / cream and stone |
| 10 | Cathedral | Civic | 26×29 B (520×580 G) | 5200×5800 | 29 B /580 G /5800 | 1 | Nave 3000 x 5000 / transept 5200 x 1000 / towers / fleche | Old tile / cream and stone |
| 11 | Cloister | Civic | 9×14 B (180×280 G) | 1800×2800 | 4.5 B /90 G /900 | 1 | Arcade / court / tiled lean-to / stone base | Old tile / cream and stone |
| 12 | Chapter house | Civic | 5×4 B (100×80 G) | 1000×800 | 5 B /100 G /1000 | 1 | Round-arched stone bays / old tile / timber roof | Old tile / cream and stone |
| 13 | Auction rotunda | Auction House | 14×14 B (280×280 G) | 2800×2800 | 17 B /340 G /3400 | 1 | Drum / 16 dome wedges / lantern / colonnade | Metal dome / cream stone drum |
| 14 | Strongroom | Auction House | 6×5 B (120×100 G) | 1200×1000 | 4.5 B /90 G /900 | 1 | Stone bay / vault / iron door / old tile | Clay tile / ochre and oak |
| 15 | Library | Library | 9×18 B (180×360 G) | 1800×3600 | 15 B /300 G /3000 | 1 | Body 2100 / buttress / round arch / square tower / hip | Old tile / cream and stone |
| 16 | Main Gate | Wall belt | 11×3 B (220×60 G) | 2200×600 | 9 B /180 G /1800 | 1 | Twin towers / 800 clear mouth / round arch / tile caps | Clay tile / ochre and oak |
| 17 | West Gate | Wall belt | 3×5 B (60×100 G) | 600×1000 | 8 B /160 G /1600 | 1 | 1000 frontage, 600 passage / round arch / cap | Clay tile / ochre and oak |
| 18 | East Gate | Wall belt | 3×5 B (60×100 G) | 600×1000 | 8 B /160 G /1600 | 1 | 1000 frontage, 600 passage / round arch / cap | Clay tile / ochre and oak |
| 19 | Ridge Gate | Wall belt | 6×3 B (120×60 G) | 1200×600 | 7.5 B /150 G /1500 | 1 | 800 passage / round arch / cap | Clay tile / ochre and oak |
| 20 | South Postern | Wall belt | 5×3 B (100×60 G) | 1000×600 | 4.5 B /90 G /900 | 1 | 400 passage / round arch / tile cap | Clay tile / ochre and oak |
| 21 | Library Gate | Library | 2×4 B (40×80 G) | 400×800 | 4 B /80 G /800 | 1 | 800 frontage, 400 passage / lintel / old tile cap | Old tile / cream and stone |
| 22 | Forecourt Gate | Auction House | 6×2 B (120×40 G) | 1200×400 | 6 B /120 G /1200 | 1 | 600 passage / round arch / iron doors / tile cap | Clay tile / ochre and oak |
| 23 | Curtain wall segment | Wall belt | 1×0.9 B (20×18 G) | 200×180 | 5 B /100 G /1000 | 2 | Stone wall / walkway / crenel / coping | None / stone |
| 24 | Wall tower | Wall belt | 3×3 B (60×60 G) | 600×600 | 7.5 B /150 G /1500 | 2 | Stone / stair core / crenel / 60 degree tile cap | Clay tile / ochre and oak |
| 25 | Precinct wall segment | Auction House; Library | 1×0.15 B (20×3 G) | 200×30 | 2 B /40 G /400 | 2 | Stone base / cream panel / coping | None / stone |
| 26 | Market stall | Trade; Square | 2.5×3 B (50×60 G) | 500×600 | 2 B /40 G /400 | 2 | Posts / 500 x 600 canvas / counter / sacks | Cream / muted-red canvas, oak |
| 27 | Stable | Wall belt | 5×4 B (100×80 G) | 1000×800 | 4.5 B /90 G /900 | 2 | Planked facade / broad door / 50 degree roof | Clay tile / ochre and oak |
| 28 | Yard shed | Wall belt; The Slums | 2×2 B (40×40 G) | 400×400 | 2.5 B /50 G /500 | 3 | Plank panel / lean-to / timber door | Old tile / smoked oak, patched plaster |
| 29 | South Bridge | River | 8×14 B (160×280 G) | 1600×2800 | 3.95 B /79 G /790 | 1 | Three round arches / piers / flat deck / parapets | None / stone |
| 30 | East Bridge | Stream | 13×5 B (260×100 G) | 2600×1000 | 2.2 B /44 G /440 | 1 | Single round arch / clear channel / deck / parapets | None / stone |
| 31 | Watermill | Fields | 4×4 B (80×80 G) | 800×800 | 4.5 B /90 G /900 | 1 | Plank / plaster / roof / 500 diameter timber wheel | Clay tile / ochre and oak |
| 32 | Windmill | Fields | 3.5×3.5 B (70×70 G) | 700×700 | 8 B /160 G /1600 | 1 | Tapered octagonal drum / cap / six sails | Clay tile / ochre and oak |
| 34 | Fountain | Square | 8×8 B (160×160 G) | 1600×1600 | 2 B /40 G /400 | 1 | Circular basin / pedestal / two stone bowls | None / stone |
| 35 | Well | Square | 2.5×2.5 B (50×50 G) | 500×500 | 1.75 B /35 G /350 | 1 | Stone ring / oak posts / tile hood / rope | Clay tile / ochre and oak |
| 36 | Statue plinth | Square | 3×3 B (60×60 G) | 600×600 | 5 B /100 G /1000 | 1 | Stepped plinth / anonymous draped silhouette | None / stone |
| 37 | Quest board | Square | 1×0.5 B (20×10 G) | 200×100 | 1.4 B /28 G /280 | 1 | Posts / plank frame / small tile hood | Clay tile / ochre and oak |

### Envelope / assembly details

- Cathedral: nave3000×5000×2600 cm, transept5200×1000×2600; two800-square towers4400 top; flèche800×400/5800 top; west front3800. Ground z0; parvis+170 does not silently raise whole cathedral.
- Town Hall:3000×2600 body1500/800-square tower3600; library1800×3600 body2100/800-square tower3000. Body envelopes include roofs; lower storeys stack320.
- Rotunda governing target: dome top3000/lantern3400 cm. Measured older greybox2200+1400=3600 conflicts; proposed22 m drum +8 dome +4 lantern matches governing silhouette. Draw the target; do not alter actor here.
- Wall:180 thickness, walkway1000. Tower variants1400 run/1500 corner **including caps**. Crenel height/top needs reconciliation before changing the wall walkway; do not silently stack a new cap above stated tower H.
- Bridges: deck+120/parapet+240 cm. South H790 from bed−550 to+240, East H440 from bed−200 to+240. South1600×2800 three arches; East2600×1000 single arch concept (greybox has two piers). Access40 cm rise in current greybox is not a canonical17 cm flight: reprofile needs separate approval within crossing envelopes.
- Watermill800-square +Ø500 wheel, river-side placement not Mill Lane. WindmillØ700/body1600 with six sails up to700 radial reach: appendage/collision review. Both are within current whole-map scope, modelled in phase E/P4.
- Stable/sheds occupy only5–9 m-deep wall-belt yards: about ten structures total, not ten of each.
- Slum representative400×400 is a whole-bay assembly example slightly below the stated420 cm nominal range; proposed420 cm frontage uses20 cm closure. Do not change the governing slum row bounds to make the preset fit.

### LOD / performance notes by type

| Types | Near | Mid / far |
|---|---|---|
| Row house, shop, inn, smithy, slum house, canonry, auction townhouse, library row | Shared facade/roof modules,3 material slots preferred,4 only shared cloth; omit hidden party sides/interiors; balcony/forge hood near only. | Simplify braces/shutters, retain jetty/offset chimney. Far roof/facade silhouette; no tiny emissive windows. Use shared instances, not unique per-building textures. |
| Cathedral, Town Hall, library | Repeated stone/cream bays; cathedral rose/tracery near plaza only; plain library buttresses; hero mass split for culling. | Preserve all landmark caps/towers/flèche; clock/tracery simplify, no silhouette disappearance. Never one monolithic300-building mesh. |
| Cloister, chapter house, rotunda, strongroom | Shared stone;16 reusable dome wedges, small lantern; only gameplay-required strongroom interior. | Dome ribs simplify, keep round drum; close bays culled outside precinct; railings/locks tiny detail removed. |
| Seven gate types, curtain/precinct walls, tower | Shared round portal, stone piers, coping, tile cap. Preserve all labelled clear passages. | Remove bevels/crenel microdetail; retain portal/tower shapes. Simple collision and segmented runs; no far LOD closes a gate. |
| Stall, stable, yard shed | Shared canvas/plank, stitch detail through material, not geometry. | Remove goods/rafters mid; far awning silhouette; no stable interior unless used. |
| South/East Bridge | Convex walking collision, openings as geometry, parapets safe without jagged invisible collision. | Keep arches open in far silhouette; remove stone bevels. No opaque box LOD hides water. |
| Watermill, windmill | Shared oak/tile/stone, spokes/sail frames near; no animation/network implementation here. | Wheel ring and sail planes remain; rope detail culls. |
| Fountain, well, statue plinth, quest board | Shared stone/oak, anonymous statue; blank papers/no lore texture. | Bowls/rope simplify; retain plinth/hood silhouette. |

Proposed budgets, not engine results: domestic8–15k near triangles,2–5k mid,300–1000 far; hero30–80k near plus instanced detail; props200–2000 near. Prefer opaque windows, no city-wide translucency. No Nanite/HLOD settings assumed or changed. Existing60 fps target must be measured on actual hardware. Architecture is static shared-world content; **no new gameplay code or replication**. Interactive gates/lights later need server-owned gameplay, not cosmetic authority.

## Actual modular modelling kit

Functional mesh stems below; future exports `SM_<Kit>_<Element>_<Variant>`. Architecture bottom-left grid pivot, props base centre; Blender metres/UE centimetres, transforms applied. W×D×H is bounding envelope; wall openings100×210/90×140 within200×320 bays. P1/P2/P3 import-and-light order remains mandatory; this concept does not authorise skipping phases.

| # | Model stem | Phase | W×D×H G | W×D×H cm |
|---|---|---|---|---|
| 1 | Wall bay warm | P1 | 20×3×32 | 200×30×320 |
| 2 | Wall bay cream | P1 | 20×3×32 | 200×30×320 |
| 3 | Wall bay planked | P1 | 20×3×32 | 200×30×320 |
| 4 | Slum wall bay | P1 | 20×3×28 | 200×30×280 |
| 5 | Corner post | P1 | 2×2×32 | 20×20×320 |
| 6 | Beam | P1 | 20×2×2 | 200×20×20 |
| 7 | X brace panel | P1 | 20×3×32 | 200×30×320 |
| 8 | Jetty band | P1 | 20×4×2 | 200×40×20 |
| 9 | Door square | P1 | 20×3×32 | 200×30×320 |
| 10 | Door round arch | P1 | 20×3×32 | 200×30×320 |
| 11 | Window leaded | P1 | 20×3×32 | 200×30×320 |
| 12 | Window shuttered | P1 | 20×3×32 | 200×30×320 |
| 13 | Shutter leaf | P1 | 4×1×14 | 40×10×140 |
| 14 | Gable end 50 deg | P1 | 20×3×12 | 200×30×120 |
| 15 | Roof slope 50 deg | P1 | 20×20×24 | 200×200×240 |
| 16 | Hip corner 50 deg | P1 | 20×20×24 | 200×200×240 |
| 17 | Roof ridge | P1 | 20×2×2 | 200×20×20 |
| 18 | Eave rafter strip | P1 | 20×4×2 | 200×40×20 |
| 19 | Lean-to roof | P1 | 20×20×12 | 200×200×120 |
| 20 | Dormer | P1 | 20×20×20 | 200×200×200 |
| 21 | Chimney | P1 | 6×6×20 | 60×60×200 |
| 22 | Balcony rail | P1 | 20×2×10 | 200×20×100 |
| 23 | Timber stair | P1 | 20×21×11.9 | 200×210×119 |
| 24 | Awning straight | P2 | 20×20×8 | 200×200×80 |
| 25 | Awning stripe | P2 | 20×20×8 | 200×200×80 |
| 26 | Stall frame | P2 | 50×60×40 | 500×600×400 |
| 27 | Counter | P2 | 20×8×10 | 200×80×100 |
| 28 | Sign bracket | P2 | 10×2×10 | 100×20×100 |
| 29 | Lantern post | P2 | 4×4×32 | 40×40×320 |
| 30 | Banner pole | P2 | 2×2×40 | 20×20×400 |
| 31 | Barrel | P2 | 6×6×9 | 60×60×90 |
| 32 | Crate | P2 | 8×8×8 | 80×80×80 |
| 33 | Hand cart | P2 | 12×20×12 | 120×200×120 |
| 34 | Bench | P2 | 20×6×9 | 200×60×90 |
| 35 | Planter | P2 | 10×10×8 | 100×100×80 |
| 36 | Stone wall bay | P3 | 20×3×32 | 200×30×320 |
| 37 | Round arcade | P3 | 20×3×32 | 200×30×320 |
| 38 | Buttress base | P3 | 10×20×32 | 100×200×320 |
| 39 | Pointed cathedral bay | P3 | 20×3×32 | 200×30×320 |
| 40 | Rose window | P3 | 80×3×80 | 800×30×800 |
| 41 | Pinnacle | P3 | 10×10×40 | 100×100×400 |
| 42 | Spire segment 60 deg | P3 | 20×20×35 | 200×200×350 |
| 43 | Gate tower cap | P3 | 60×60×52 | 600×600×520 |
| 44 | Dome wedge 1 of 16 | P3 | 55×140×80 | 550×1400×800 |
| 45 | Coping / crenel | P3 | 20×18×10 | 200×180×100 |
| 46 | Kerb | P4 | 20×4.5×1.2 | 200×45×12 |
| 47 | Parvis stair | P4 | 20×30×17 | 200×300×170 |
| 48 | Bridge arch bay | P4 | 80×160×79 | 800×1600×790 |
| 50 | Mill wheel | P4 | 50×5×50 | 500×50×500 |
| 51 | Windmill sail | P4 | 10×3×70 | 100×30×700 |

Composite P2 props use this vocabulary: well hood/stone ring, fountain basin/bowls, statue/plinth, quest-board frame/papers, strongbox, sack pile. P5 overlays: leaves, crack, moss, forge soot, water patch, worn paint, plaster repair, wheel tracks. No textures created. P4 landscape is part of V3, not cancelled: three tree canopies, shrub, ivy, dirt/grass seam modules and both bridges. Vegetation stems need final crown sizing before modelling; cap canopies at three, not a new forest budget.

**Precision:** building envelopes/setout values are10 cm multiples. Kerb is the owner-approved **45×12 cm section**, within150 cm kerb zone; its200 cm run snaps10 while cross-section explicitly uses canonical finer detail dimensions (4.5/1.2 G). Stair prescribed exception17 cm rise/30 tread,119 cm seven-rise or170 cm ten-rise. Tile course26 and cobble20–25 are surface-detail dimensions, not pivot snap spacing.

**Pitches:**50°/60° are exact surface targets;120/240/350/520 cm in table are rounded roof bounding envelopes, not exact slope rises. Roof shape stays at exact pitch inside/under its envelope with an end/ridge closure; seam pivots/eave spacing snap10. A2 m run at50° rises238.35 cm, not240 exactly. Gable wedge200 width uses100 half-run, rise119.18 inside120 envelope. Confirm this envelope convention before fabrication; no silent pitch change. Dome radial wedge22.5° increment is a radial piece inside a Cartesian bounding box.

**Proposed closure addition:**10 cm-increment width infill,30 depth,320/280 height, plain or planked, no resized fixed openings. Avoid slivers under40 unless hidden against party wall. This resolves non-bay actor widths without moving blocks. Kit sheet shows main vocabulary, not every closure permutation.

## Open questions / proposed doc changes — not applied

1. Confirm ADR-019/020 proposed look/texture policy: grounded painterliness, six families,3-canopy cap; unique plaza/cathedral facade exception only if a real need arises. No new palette keys proposed.
2. Clarify whole200 cm bay wording versus620 cm minima/non-bay measured fronts: recommend200 cm bays plus10 cm closure panels. Whole-bay-only regrouping is a separately approved layout change; do not move rows for this art.
3. Clarify grid means **setout/pivots**, not every mesh bound: approved45×12 kerb,17 cm stair,26 cm tile and exact pitched roof geometry remain exact detail dimensions. No kerb size change proposed; owner's correction already governs.
4. ~~Auction dome~~ **Decided 2026-11-16: follow the plan** — 30 m dome / 34 m lantern; reconcile the older 36 m greybox mass in the Editor (proposed 22+8+4).
5. ~~Arches~~ **Decided 2026-11-16: round arches** on civic, library, gates and strongroom; pointed Gothic arches on the cathedral only. Library pyramid tower is not a spire.
6. Confirm wall walkway10 m versus overall crenel silhouette; tower14/15 and gate15–18 include caps. Do not lower walkway or stack additional caps silently.
7. Decide bridge access reprofile from current40 cm risers to walkable17 cm stairs within existing footprints; confirm single East arch versus two current greybox piers. Optional extra slum bridge is **not drawn or authorised**.
8. ~~Docks~~ **Decided 2026-11-16: no docks.** Still open: windmill footprint/sail sweep during phase E.
9. Approve inn/smithy as existing row replacements, chapter-house location within cathedral precinct and anonymous statue/neutral banners until ORIGINAL lore in DESIGN. No named lore invented.

## Validation and eventual Editor test

Sheet status (2026-11-16): all nine sheets are painterly concept studies in one shared style; the district, building and kit sheets show back alleys, and composed views state on the sheet where camera height or depth is bent for readability. Every SVG parses as XML and every `index.html` link resolves. That is not a Development Editor build or an engine performance claim; no C++ or binary assets changed.

When Editor/MCP available: import one P1 bay/door/eave/roof beside180 cm pawn. Verify100/200 scale,320/280 stacking,10 cm pivots, no6 m seams, exact50/60 pitches,45×12 kerb and1.5 m walk clearances. Assemble a single live plot using its measured bounds/closure infill before replacing rows. Capture V1–V7 with governing poses: cathedral hierarchy, open axis, quiet library, slum below wall, actual water from bank not on-axis, both bridge transitions/navmesh. Confirm cap heights and doorstep collision before expanding. Re-run measured layout audit after approved replacements; measure frame time and LOD transitions. Do not call this concept engine-verified.
