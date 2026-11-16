# City Layout — Starter City

Status: **Revision C, 2026-11-15 — freeze candidate, needs owner sign-off** (ADR-025).
Companions: `ART_DIRECTION.md` (the look), `ART_PIPELINE.md` (the kit), `DECISIONS.md` (ADR-013/014/015/016/021, superseded where noted).

This document owns **where things are and how big they are**. It does not own what they look like. It is the **governing document** for the city: where any other doc disagrees on layout, scale or counts, this one wins (and the other doc gets fixed). `LVL_StarterVillage_V3` is the current map built from it.

**Sources of truth**

| Artifact | Path | Edited by |
|---|---|---|
| Every number in this document | `Data/Layout/city_layout.csv` | hand, then regenerate |
| The plan drawing | `Docs/Layout/CityPlan.svg` (+ `.html`) | `Tools/Layout/build_city_plan.py` |
| The layout check | printed by the same script | — |

If this document and the CSV disagree, **the CSV wins** — then fix the document.

```
python Tools/Layout/build_city_plan.py
```

The script writes the drawing, prints the district/building summary, and exits non-zero if any block leaves the wall, two blocks overlap, or a street runs through a block. At the time of writing it reports **clean**: 37 block rows, **300 street buildings**.

---

## 1. The number

| | Value | Note |
|---|---|---|
| **Playable map** | **420 × 330 m** (13.9 ha) | X −210…+210, Y −165…+165 |
| **Walled town** | **300 × 200 m** (6.0 ha) | X −150…+150, Y −100…+100; the wall polygon in §4 |
| Market square | 80 × 60 m (4,800 m²) | 8% of the town; the largest open space by far |
| Auction forecourt | 56 × 58 m | Walled; the rotunda's close |
| Street centreline | ≈1,350 m inside the walls | plus ≈656 m outside: approaches, Mill Lane, the slum lane and alleys |
| Street buildings | **300** in 37 rows | one per ~54 m² of block ground |
| Landmarks | 13 | Cathedral, town hall, rotunda, library, gates, bridges… |
| Wall-belt sheds | ~10 (not modelled yet) | Stables and yards against the wall |
| **Total structures** | **~310** | |

**Why the town is 300 × 200 and the map is bigger.** The owner's brief: *"the maps scale should be about 300x200 meters"*, then *"300x200 should be the town alone"*. So the **walled town is exactly 300 × 200 m**, and the map grows to 420 × 330 m to hold what a walled town needs and cannot contain: the river and its bridge, the slum suburb outside the south gate, the fields and mill to the west, and the ridge with the waterfall to the north-east. 60 m of ground beyond each wall face is enough for all four without the town shrinking to pay for them.

**Consequence, stated plainly:** this is a bigger town than the revision-B plan (216 × 142 m) and much bigger than the old `LVL_StarterVillage_V2` greybox (a 400 m ring of scattered actors). The wall moves, the districts all move, the river moves, and the slums leave the walls entirely. V2 was therefore **rebuilt from this plan** as `LVL_StarterVillage_V3` (§13), the current map; the old level is kept for comparison.

---

## 2. Coordinate frame

Everything in this document and in the CSV is in **metres**.

| Axis | Direction | Notes |
|---|---|---|
| **+X** | **east** | −210 (map west edge) … +210 (map east edge) |
| **+Y** | **north** | −165 (map south edge) … +165 (map north edge) |
| **+Z** | up | **0 = the market square paving** |
| Origin | `(0, 0, 0)` = the **market fountain** | Every distance in §12 is measured from here |

- Unreal uses centimetres: multiply by 100 (`300 m` = `30000 uu`). Place the level's origin so the fountain sits at world `(0, 0, 0)`.
- **North is +Y**, so the plan draws like a map (north up) and "north wall" always means the high-Y wall.
- Yaw: `0°` = +X (east), `90°` = +Y (north). UE yaw matches this, so a camera at yaw 90 looks north.
- The plan drawing covers the whole map at **10 m grid / 50 m majors**, coordinate ticks in metres, and dimension lines for both the 420 × 330 m map and the 300 × 200 m town.

---

## 3. What the reference decides

The owner's aerial concept (save it as `Art/Reference/REF_CityOverview_Aerial_01.png`) is the layout's source image. Read against the five districts in ADR-014, it settles these:

| In the reference | Decision here |
|---|---|
| One huge Gothic cathedral, top centre | **The cathedral** on the north axis, west front facing the square. The only silhouette above 40 m. |
| Round red building with a dome, right of centre | **The auction rotunda** (Ø 28 m) inside a walled forecourt, east. |
| Large fountain square, centre | **80 × 60 m market square** at the origin. |
| A second large spired church, upper left | **Dropped as a separate building.** Its role is taken by the cathedral's cloister and chapter house in the cathedral precinct. One landmark, one spire. |
| Dense red roofs everywhere, buildings touching | **Rows, not plots**: blocks are continuous frontages with no gaps wider than 1 m. 300 buildings fill the 300 × 200 m core. |
| Wall with towers, gates fore and aft | **Curtain wall, 13 towers, 6 gates** (4 land, 1 postern, 1 library precinct gate), §4. |
| River along the bottom, big arched bridge at the south gate | **River outside the south wall**, 16 m wide, 28 m three-arch bridge on the south axis. |
| Stream and waterfall at the top right | **East stream** off the **ridge**, ~22 m fall, single-arch bridge at the east gate. |
| Shanty roofs, bottom of the image | **The slums** are a suburb **outside** the south wall, on the flood plain, between the bridge and the main gate. |
| Fields, mill, windmill, bottom left | **South-west fields** with the watermill on the river and the windmill on the knoll. |
| Mountains and haze beyond the walls | Map edge closed by fields, the river and the ridge (+22 / +30 m terraces). No fog in the streets. |

Deliberate departures: the reference's streets wander; ours are a legible four-axis network plus lanes, because a town a player must navigate without a map needs a readable skeleton (ADR-015) — the lanes and the irregular block depths supply the medieval looseness.

---

## 4. Wall, towers, gates

Curtain wall polygon (outer face), clockwise from the south-west:

```
(-150,-100) → (-150,80) → (-126,100) → (126,100) → (150,80) → (150,-100) → close
```

300 m along the south wall, 252 m along the north, 180 m along each side wall, with chamfered NW and NE corners (31.2 m each). Wall run **≈974 m**, **1.8 m thick**, walkway at **10 m**. Thirteen towers, **6 × 6 m**, **15 m** at the corners and **14 m** on the runs.

| Gate | Position | Opening | Role |
|---|---|---|---|
| **Main Gate** (south) | `(0, -100)` | 8 m, twin towers, portcullis; 22 m wide, 18 m tall | The arrival. Everything in §11 V1 is framed through it. |
| **South Postern** | `(95, -100)` | 4 m, 9 m tall | The slums' back door into the town; short cut to the library lane. |
| **West Gate** | `(-150, -2)` | 6 m, 10 m wide, 16 m tall | High Street; cart traffic to the fields. |
| **East Gate** | `(150, -2)` | 6 m, 10 m wide, 16 m tall | High Street; the stream bridge is 6 m beyond. |
| **Ridge Gate** (north) | `(70, 100)` | 8 m, 12 m wide, 15 m tall | Foot traffic to the waterfall terrace. Offset east because the cathedral abuts the north wall — see §16. |
| **Library Gate** | `(94, -58)` | 4 m, 8 m tall | Off Library Lane into the library precinct. A precinct gate, not a curtain-wall gate. |

Rules:
- The wall is continuous except at the gates; the north wall is **solid behind the cathedral** (the chancel backs onto it). No gate may be cut there — it would open into the building and break both hero views.
- Towers sit at the four corners, at the two chamfers, at three points along the north run, two on each side wall, and flank every land gate. No tower is taller than the gatehouse except the corner towers.
- The wall belt inside is sheds, stables and yards, 5–9 m deep, not streets. Buildings may lean on the wall; nothing may cross it.

---

## 5. Districts

Five districts, as accepted in ADR-014, re-cut to this plan. They are **zones for character and budget**; streets, the square and the wall belt are not districts.

| # | District | Key | Extent (m) | Rows | Buildings | Height band | Landmark |
|---|---|---|---|---|---|---|---|
| 1 | Cathedral & Town Hall | Civic | X −76…44, Y 30…96 (120 × 66) | 5 | 35 | 8–58 m | **Cathedral** (58) + **Town Hall** (36 tower) |
| 2 | Trade District | Trade | west third + the south band (L-shape) | 16 | 158 | 9–16 m | — (the High Street is its landmark) |
| 3 | Auction House | Auction House | X 44…150, Y −20…96 (106 × 116) | 3 | 32 | 8–34 m | **Rotunda** (34 lantern) |
| 4 | The Slums | The Slums | X −124…106, Y −126…−100 (230 × 26) | 12 | 61 | 3.5–7 m | — (the wall, and the river behind it) |
| 5 | Library | Library | X 94…150, Y −96…−20 (56 × 76) | 1 | 14 | 5–30 m | **Library** (30 tower) |

**Height ladder — this is the rule that keeps the town readable at a glance:**

```
cathedral flèche 58
  cathedral west towers 44
    town hall tower 36
      auction lantern 34  ≈  library tower 30
        cathedral body 26, gatehouses 15–18
          trade rows 9–16
            slums 3.5–7
```

- Nothing in the slums may exceed the lowest trade row. Nothing but the cathedral may exceed 40 m.
- District identity is carried by **height and density first, material condition second** (ADR-019): only the Civic district gets clean dressed stone; only the Auction rotunda gets visible metalwork; the slums are the only *worn* surfaces.
- The library is **walled off** from the town by its precinct wall along X 96 — that contrast is the point of putting it beside the auction quarter.
- The slums stand **outside the wall** on the flood plain. They are the only district the wall does not enclose, and the only one the player walks through before entering the town.

**Block rows** are buildable bands, not parcels. Each holds 1–2 rows of buildings depending on depth; the counts above are the budget. Massing variety within a row is generated (ADR-016), not authored. Rows deeper than 17 m are drawn with a courtyard and are two rows back-to-back; shallower rows are a single frontage.

---

## 6. Streets

Twenty-two centrelines. Widths are **between building lines, kerb zones included**; the carriageway is width − 3 m.

| Street | Class | Width | Route | Paving |
|---|---|---|---|---|
| **High Street (west)** | high street | 10 m | West Gate `(-150,-2)` → square `(-44,-2)` | grey setts, kerbed |
| **High Street (east)** | high street | 10 m | square `(44,-2)` → East Gate `(150,-2)` | grey setts, kerbed |
| **Ceremonial Approach** | ceremonial | 20 m | square north edge `(0,30)` → parvis steps `(0,33)` | dressed stone apron, no kerbs |
| **South Spine** | spine | 10 m | Main Gate `(0,-100)` → square `(0,-30)` | worn setts, kerbed |
| **Ridge Road** | ring | 8 m | Ridge Gate `(70,100)` → `(70,84)` → `(104,72)` → `(116,52)` → `(116,-2)` | setts, kerbed |
| **West Ring** | ring | 6 m | `(-138,-96)` → `(-138,92)` | setts, kerbed |
| **Dyer Lane** | lane | 5 m | `(-146,64)` → `(-44,64)` | worn setts |
| **Cooper Lane** | lane | 5 m | `(-146,32)` → `(-78,32)` | worn setts |
| **Fullers Lane** | lane | 5 m | `(-146,-36)` → `(-44,-36)` | worn setts |
| **Tanners Lane** | lane | 5 m | `(-146,-68)` → `(90,-68)` | worn setts |
| **Weavers Lane** | lane | 4.5 m | `(-114,-96)` → `(-114,66)` | worn setts |
| **Library Lane** | lane | 5 m | `(92,-96)` → `(92,-20)` | worn setts |
| **Slum Lane** | lane | 4 m | `(-122,-112)` → `(104,-112)` | ragged setts, no kerb |
| **Slum alleys** ×4 | alley | 3 m | X −88, X −46, X 46, X 82, from Y −126 to −100 | ragged, no kerb |
| **Mill Lane** | dirt | 5 m | bridge `(0,-140)` → `(-50,-136)` → mill `(-92,-130)` | dirt, unlit |
| **Approaches** ×3 | dirt | 8 m | South `(0,-165…-100)`, West, East | dirt, worn setts at the gate |
| **Ridge Path** | dirt | 4 m | Ridge Gate → `(80,122)` → `(96,140)` | dirt, footpath |

Rules:
- **Four axes, one hierarchy.** The High Street is one continuous east–west line, interrupted only by the square: it enters at `±44`, 4 m outside the square's edge, and the square's paving takes over between. It passes 8 m south of the fountain's edge — not through the square's centre.
- The **north axis is the ceremonial approach**: square → 10 steps → parvis → cathedral west front. It is the widest clear sightline in the town and nothing may be placed in it.
- The square has **no kerbs inside**; the four streets meet its edges at their own centrelines, deliberately 4 m out of alignment. That offset is period-correct and invisible across 80 m.
- Lanes are 4–5 m (one cart), alleys 3 m (one person and a handcart). Nothing wider than 6 m outside the town's three approaches.
- **Kerb: 45 cm wide × 12 cm high**, 1.5 m kerb zone at each street edge, 0.5% camber. **Owner decision, 2026-11-15** — it closes ADR-021's open item: a 12 cm kerb is step-up-able without a mantle, and reads as a kerb rather than a low wall from player height. `ART_PIPELINE.md` §2 and ADR-021 carry the number.

---

## 7. Market square

X −40…40, Y −30…30 (80 × 60 m). One paved surface, **no kerbs inside**, 8 m minimum clear ring at the fountain.

| Element | Position | Size |
|---|---|---|
| Fountain | `(0, 0)` | basin r 8 m, total height 4 m |
| Statue on plinth | `(-18, 12)` | r 3 m, 10 m tall |
| Well | `(-30, -20)` | r 2.5 m, 3.5 m |
| Market stalls ×10 | perimeter, see CSV | 5 × 6 m awnings, no lettering |
| Quest board | `(16, 18)` | under the parvis steps |
| Entrances | `(-40,-2)`, `(40,-2)`, `(0,-30)`, `(0,30)` | 10, 10, 10, 20 m |

The square is the only place in the plan with **no kerb, no wall and no gate** — it must feel like one room. Stalls leave a 12 m clear cross through the middle (north–south and east–west) so the fountain and the cathedral front stay visible from every entrance.

---

## 8. Landmarks

| Landmark | Footprint | Height | Notes |
|---|---|---|---|
| **Cathedral** nave | 30 × 50 m, `(-15,48)`…`(15,98)` | 26 m | Flat east end against the north wall; no apse beyond it |
| Cathedral transept | 52 × 10 m at Y 68…78 | 26 m | Gives the cross plan seen from the air |
| West towers ×2 | 8 × 8 m at X ±15, Y 40…48 | **44 m** | The west front faces the square; the only towers on that axis |
| Crossing flèche | 8 × 4 m at the crossing | **58 m** | The town's single tallest point |
| **Town Hall** | 30 × 26 m, `(-74,34)`…`(-44,60)` | 15 m | 3 storeys + attic; door south onto its forecourt |
| Clock tower | 8 × 8 m at the SE corner | **36 m** | Reads the hour from the square |
| **Auction rotunda** | Ø 28 m at `(80,40)` | 30 m, lantern **34 m** | Colonnaded drum, dome, the only metalwork |
| Strongroom | 12 × 10 m at `(94,20)`…`(106,30)` | 9 m | Vaulted, the only locked interior |
| **Library** nave | 18 × 36 m at `(112,-92)`…`(130,-56)` | 21 m | Buttressed; north–south |
| Library tower | 8 × 8 m at the SW corner | **30 m** | Square, pyramid cap |
| Cloister | 18 × 28 m at `(-40,56)`…`(-22,84)` | 9 m | Cathedral precinct; the former "parish church" role |
| South Bridge | 16 × 28 m at `(0,-152)`…`(0,-124)` | deck 0 | Three arches, flat walkway, piers in the river |
| East Bridge | 26 × 10 m at `(150,-7)`…`(176,3)` | deck 0 | Single arch over the stream |
| Watermill | 8 × 8 m + 5 m wheel at `(-96,-128)` | 9 m | On the river bank below the slums, off Mill Lane |
| Windmill | Ø 7 m, 6 sails at `(-176,-160)` | 16 m | On the knoll in the south-west field |

Cathedral detail that the plan fixes (the look is `ART_DIRECTION.md`): a **38 m wide west front** (30 m nave, towers projecting 4 m each side), two 44 m towers, a rose window between them, and a 58 m flèche. It is the only building allowed pointed arches, pinnacles and a rose window.

---

## 9. Water and terrain

| Surface | Z (m) | Note |
|---|---|---|
| Market square, all streets, all blocks | **0** | **One ground constant for the whole walled town** (ADR-016). No terraces inside the walls. |
| Cathedral parvis | **+1.7** | 10 risers at 17 cm, 30 cm treads, Y 30…33 |
| River water | **−4.5** | Bed −5.5; 16 m channel; banks slope from −3.0 at the wall foot |
| Stream water | **−1.0** | 10 m cut outside the east wall, x ≈ 169, bed −2.0. §9's +2.0 assumed a carved landscape; the blockout town is one plane at 0, so the stream sits in a cut until phase E gives it a channel profile |
| Waterfall pool | **−1.0** | At `(168, 86)`, r 9 m; the fall drops from the ridge terrace at +22 |
| Ridge | **+22 / +30** | Two built terraces 64 × 70 m and 52 × 42 m; the fall cuts their south face at X ≈ 168 |
| Bridge decks | **+1.2** | Deck + parapet (−0.8…+1.2 m body, parapets to +2.4) with three 0.4 m steps up each bank |
| Fields | **−1.5** to −0.5 | Gentle, no walkable cliffs |
| Map edge | — | Invisible wall + kill volume at ±210 / ±165; hills and water beyond |

- **River**: 16 m channel, centreline `(-210,-150) → (-120,-142) → (0,-138) → (120,-150) → (210,-156)`. It runs **outside** the south wall, 38 m from it at the closest, and the slums stand on its north bank. The only crossing is the South Bridge on the town's axis.
- **Stream**: 8 m channel at X ≈ 168 (built in V3 as a 10 m cut, see the table above), from the fall `(168,92)` south to the river `(176,-154)`. The East Bridge carries the High Street over it 6 m outside the East Gate.
- **Waterfall**: ~22 m fall from the low ridge terrace (+22) into the pool (−1.0), 16 m wide (X 160…176), visible from the Ridge Gate and from the ridge path.
- **Mill**: on the north bank at `(-96,-128)`, wheel in the river, served by Mill Lane. The reason the lane exists.
- **Navmesh** covers the walled town, both bridges, the approaches, the slum lane and the fields. The river, the stream below the fall, the pool and the ridge scree are excluded.

Why the town is flat: a stepped town inside the walls triples the navmesh and collision work and makes every block's base conditional (the exact bug ADR-016 closes). The vertical interest is supplied by the **parvis**, the **wall**, the **roofline**, the **ridge** and the **river cut** outside — all of which read at player height.

---

## 10. Density and massing rules

These are what make the plan produce the reference's look. They are rules for the generator and for anyone placing kit pieces by hand.

| Rule | Value |
|---|---|
| Bay module | 2 m; buildings are whole bays (3–7 bays = 6.2–14 m frontage) |
| Storey height | 3.2 m (2.8 m in the slums) |
| Block frontage | continuous; **no gap wider than 1 m** between buildings in a row |
| Rear yards | 3–6 m behind the front row; a lane or a wall behind that |
| Back alleys | **Owner decision 2026-11-16:** every district gets back alleys behind its rows (dark, run-down — see `ART_DIRECTION.md`). Not yet in the CSV: add them as `street` rows of class `alley` on the machine that holds `Data/Layout/city_layout.csv`, re-run the check, then rebuild V3 |
| Jetty | upper storey overhangs 0.4 m on the street face, never on the sides |
| Roof pitch | 50° domestic, 60° towers; ridge parallel to the street except on corner plots |
| Chimney | one per building, offset from the ridge |
| Slums | yaw ±10°, footprints 4.2–9.4 m, heights 3.5–7 m, lean-tos into the alleys |
| No two neighbours | share both footprint and height |
| Right of way | a player must never have to walk on the road to pass a cart; 1.5 m clear sidewalk minimum |

Coverage, checked against the CSV: blocks are 27% of the town (16,283 m² of block ground for 300 buildings, ~54 m² each), streets 16%, landmarks and their precincts 9%, the square 8%. The rest is yards, walls and wall belt — deliberately uneven, so the roofs have gaps and shadow between them.

---

## 11. Sightlines (the seven capture views)

Positions are `(x, y)` at **eye height 1.65 m** unless raised. These are M6-13's captures and the test of the whole plan: if any of these is wrong, the layout is wrong.

| # | View | Pose | Must show | Fails if |
|---|---|---|---|---|
| **V1** | Gate arrival | `(0,-148)` yaw 90 | Bridge deck, slum roofs, gate arch (48 m), spine, fountain (148 m), cathedral front **196 m** away | Anything blocks the axis; the gate reads as a hole, not a gate |
| **V2** | Square centre | `(0,-24)` yaw 90 | Fountain, steps, both west towers, rose window | The flèche is hidden; the front is off-centre |
| **V3** | High Street | `(-140,-2)` yaw 0 | 96 m of shopfronts to the square, town hall + clock tower on the left | The street reads as straight and empty; no height change |
| **V4** | Auction approach | `(70,10)` yaw 90 | Forecourt gate, wall, dome at 30 m | The dome is not framed by the gate |
| **V5** | Slum lane | `(-30,-112)` yaw 90 | 7 m roofline below the 10 m wall, laundry, worn paving, the town's roofs beyond | The slums read as small trade houses |
| **V6** | Library court | `(140,-64)` yaw 180 | Buttressed nave at 10 m, tower above, precinct wall | It reads as a barn; the close is not quiet |
| **V7** | Parvis look-back | `(0,42,3.35)` yaw 270 | Whole town falling away: square, trade roofs left, slums and river beyond the gate | The town reads flat; the wall is invisible |

V1 and V7 are the two that sell the scale. V1 is the first thing a player sees; V7 is the reward for climbing the steps.

---

## 12. Player flow and gameplay anchors

| Anchor | Position | Why there |
|---|---|---|
| **Player start** | `(0,-160)`, facing north | South bank, 8 m short of the bridge: the arrival shot before any input |
| Quest board | `(16,18)` | North-east of the fountain, on the way to the parvis |
| Class trainer | `(-56,30)` | Town hall forecourt, beside the civic door |
| Vendor | `(-80,4)` | High Street north side, awning out |
| Forge | `(-122,-44)` | Workshop row against the west wall: smoke, red, the only fire inside the walls |
| Auction entrance | `(70,16)` | Forecourt gate on the High Street |
| Library entrance | `(94,-58)` | Off Library Lane, at the precinct gate |
| Cathedral west door | `(0,48)` | Head of the parvis steps |
| **Mill Bank** encounter | `(-72,-126)` | Outside the wall, on the slum's river edge: 3 brutes, no gate to hide behind |
| **Ridge Terrace** encounter | `(152,60)` | Above the waterfall: 2 casters + 1 brute, high ground |
| Watermill | `(-96,-128)` | River bank below the slums |
| Windmill | `(-176,-160)` | The field knoll; visible from the bridge |

Distances from the fountain: south gate 100 m, cathedral door 48 m, trainer 63 m, vendor 80 m, auction 72 m, library gate 110 m, forge 130 m, west and east gates 150 m.

The loop this produces: spawn **60 m** south of the gate and 8 m short of the bridge → 28 m over the deck → 24 m through the slums → the gate → 100 m up the spine to the fountain → quest board 20 m from the fountain → out of the gate to Mill Bank → back → trainer at the town hall → vendor on the High Street. **Every service is within 130 m of the fountain; every fight is outside the walls.** That is the whole of M7's first playable in one sentence, and the reason the town is this compact.

---

## 13. Build phasing

| Phase | Contents | Size | Exit |
|---|---|---|---|
| **A — setout** | Rebuild the greybox from this CSV: ground cut for the river, wall, gates, 22 streets, square, **300 individual buildings** | L | The plan and the level agree: `LVL_StarterVillage_V3`, 499 blockout actors |
| **B — civic** | Cathedral (nave, transept, towers, flèche), parvis + steps, town hall + clock tower, cloister, canonry | L | V2 and V7 pass in greybox |
| **C — east** | Auction rotunda, forecourt + walls + gate, strongroom, AQ rows, library + precinct | M | V4 and V6 pass |
| **D — rows** | Trade 158, slums 61, auction 32, civic 35, library 14 | XL | V1, V3, V5 pass; coverage reads as a town |
| **E — water & land** | River, banks, bridges, stream, fall, fields, mill, windmill, ridge | M | V1 has water under it; the map edge is closed |
| **F — detail** | Yards, wall-belt sheds, cemetery, slum lean-tos | M | No grey primitive visible inside the walls |
| **G — light, decals, navmesh** | M6-10…M6-14 | M | 60 fps, enemies path gate → plaza |

A–D are the layout becoming real. E–G are the art pass the roadmap already owns. Nothing in B–F may move a wall, a gate or an axis: those are frozen by this document, and moving one means re-running the check and re-approving the seven views.

**Phase A state (2026-11-15).** `LVL_StarterVillage_V3` **is the project's game map**: `Game/Config/DefaultEngine.ini` sets both `GameDefaultMap` and `EditorStartupMap` to it (revert line is in the file's comment). Boot verified from project defaults — Play on V3 spawns the `BP_ThirdPersonCharacter` at the `PlayerStart` (0,-160) facing north, `AGodDomainGameMode` logs a clean match start, 499 greybox actors load, no errors in the log, and a 1.65 m sightline trace from the spawn runs 60 m through the south gate to the square without hitting anything (the control trace at x -20 hits the slum row at 16 m). **To reproduce: open the project and press Play** — V3 loads and you stand on the south bank, three steps below the bridge deck, looking through the gate.

![Arrival at the south gate](Layout/Level_Arrival_V3.png)

*The arrival frame at eye height at the spawn, 59 m short of the gate: three steps up to the bridge deck and its parapets, the slum rows outside the wall, the south gate open, and the spine running through it to the fountain. `Layout/Level_Town_V3.png` is the whole setout in one oblique — river, both bridges, wall, slums, town, cathedral, ridge; `Layout/Level_Top_V3.png` is the plan grid from directly above (**south at the top**, east at the right — Unreal's axes are left-handed, so a north-up capture would mirror the plan; this one is the plan turned 180°); `Layout/Level_Gate_V3.png` shows the wall and the 8 m passage head-on; `Layout/Level_River_V3.png` the channel from the bank; `Layout/Level_Arrival_V3_PIE.png` is the Play-In-Editor capture with the pawn in frame.*

The setout is built to **read**, not only to measure. Four things changed after the first pass was walked:

- **Every block is an array of individual buildings**, not one box with its middle cut out: **300 of the 499 actors are single buildings** — one per `count` column of the CSV, in a regular row with a 40 cm party gap, heights 3.5–7 m in the slums and 9–16 m in trade. Each is named `<block>_<row><index>` (`SL-4_103` is the fourth plot of the second row of Slums block 4), so replacing one with a model touches nothing else, which was the point of splitting them.
- **The river and the stream are real channels.** The ground is cut along the river's own centreline in 14 slices, with a bed 1 m under the water and the surface at −4.5 m; the stream runs in a 10 m cut outside the east wall from the pool to the river. Street pads are clipped at every crossing, so no road floats over a channel (a whole-route pad used to lid the river at ground level and hide the bridge completely).
- **Both bridges are bridges**: deck at +1.2 m, three 0.4 m steps up each bank, parapets, two piers. From the south bank you climb onto it; from the water you see its openings.
- **The ridge is two terraces** (+22, +30) with the 16 m-wide, ~22 m-tall waterfall on their south face and the pool at the foot — it was one unexplained 80 x 85 m slab.
- **Colour, so the setout is legible**: eight material instances (ground, ridge, town, slum, stone, paving, water, landmark) on duplicated cube/cylinder/sphere meshes under `Content/StarterVillage/Greybox/{Materials,Meshes}`. One material per category, no textures — the art pass replaces them.

`Tools/Editor/build_level_v3.py` generates all of it from the CSV through the editor's MCP server, in folders under `GD/Greybox`, and re-running it with `--clear` rebuilds idempotently. The template's 80 m floor and its brush were removed, and the PlayerStart moved to `(0,-160)` facing north. What is still approximate: the town is one flat plane, so the stream sits in a cut rather than the raised watercourse §9 describes, and the buildings are single boxes — no roofs, jetties or gables until M6-04.

**Measured against the plan (2026-11-15).** `Tools/Editor/compare_level_to_plan.py` reads every greybox actor's bounds out of the editor and compares them with this CSV — **118 checks, 118 pass, 0 flagged**. The artefacts are `Layout/Level_vs_Plan.md` (the tables: plan value, built value, delta) and `Layout/Level_vs_Plan.svg` (this plan in blue, the built level in orange, on one 30 m grid, with a numbered pin on every gate, bridge, district and landmark and its measured value in a legend band). What it pins down:

| | measured |
|---|---|
| Wall | ±150.9 × ±100.9 outer, **1.8 m thick**, 10 m tall, 8 runs (6 segments less the gate mouths, plus 2 chamfers), 13 towers |
| Gate passages | Main 8.00 m, West 6.00, East 6.00, Ridge 8.00, Postern 4.00, Forecourt 6.00 — all clear |
| River | surface −4.55 both crossings (plan −4.5), **16.0 m wide**, centre −138.0 at the Main Gate; banks dry at ±9 m |
| Bridges | South 16 × 28, East 26 × 10, decks +1.20 m, **6 risers each at 0.4 / 0.8 / 1.2**, 2 piers, 2 parapets |
| Roads | spine 10.0, approach 8.0, High Street 10.0, Ridge Road 8.0 (traced across, it is diagonal), West Ring 6.0; 22 pads |
| Districts | slums, trade, civic, auction, library extents within **0.2 m** of the plan |
| Cathedral | west front **38.0 m**, two 44 m towers, **58 m flèche** (the town's tallest point), nave on z 0 |
| Auction House | Ø**28.0** drum at (80, 40), 22 m drum + 14 m dome, forecourt gate at (70, 6) |
| Ridge | +22 and +30 terraces, 64 × 70 and 52 × 42, 22 m fall sheet at x 160…176 |
| Views | PlayerStart (0, −159): **59 m** to the gate wall, **195 m** to the cathedral parvis |
| Block array | 37 blocks, **300 buildings**; slums 12 / 61, trade 16 / 158, civic 5 / 35, auction 3 / 32, library 1 / 14 — every count **exactly** the CSV's |
| Block regularity | within a row every plot is identical to **1 cm**; party gap **0.40 m** throughout (min and max); built footprint **0.20 m** inside the plan edge (the half gap) |
| Block placement | **0** blocks on a street corridor, **0** floating above z 0, and every frontage within **0.3 m** of the plan's own distance to its nearest street |
| Block pitch (centres) | slums 14 m across, auction 79 m, trade 30–69 m; every centre on its plan block within 0.3 m |

Two things the measurements *cannot* deliver, recorded here so nobody re-litigates them as bugs:

1. **The stream is 3 m below the plan's level** (§9 asks +2.0 water, +6.0 pool; the level builds −1.0 in a 10 m cut). It is not fixable by a setout parameter: the plan also fixes the **East Approach at 0 m**, running through the same crossing the stream passes under, and the East Bridge deck is +1.2. Water at +2.0 would flow two metres above the road it is bridged over and swallow its own deck. The +2.0 figure only holds if the ground east of the wall rises with the foot of the ridge — the phase-E terrain item. The cut is the only self-consistent reading of the plan's own sections until then.
2. **The on-axis arrival cannot show the river, and does not need to.** A ray from the PlayerStart to the river on the axis is stopped by the **bridge at 8.3 m** — the water is 6 m below the bank, 14 m ahead, behind a 16 m wide deck. The plan's own V1 note lists *bridge deck, slum roofs, gate arch* for a reason. The water is shown by `Layout/Level_River_V3.png` (from the bank, channel + both banks + bridge) and by `Layout/Level_Town_V3.png` (the whole city from the air).

---

## 14. What this changes

| Document | Change |
|---|---|
| **ADR-013** (river town on terraces) | Geometry **superseded**. One river outside the south wall, one stream outside the east wall, flat town inside. The terrace idea is not coming back. |
| **ADR-014** (five districts) | Districts **kept**, extents and positions **superseded** by §5. The parish church is **merged** into the cathedral precinct as the cloister/chapter house — the town has one spire. |
| **ADR-015** (streets, ground profile) | Street hierarchy and the carved-road logic **kept**; the terrace profile is **dropped** (§9); the network is **superseded** by §6. |
| **ADR-016** (massing variety) | Ranges **kept and extended** in §10; district extents superseded. |
| **ADR-021** (ground kit) | **Kerb height closed at 12 cm** (45 cm stone, 1.5 m zone). |
| **`ROADMAP.md` M6-01** | This document is the freeze candidate; M6-01 becomes "sign off revision C and rebuild the greybox". |
| **`LVL_StarterVillage_V2`** | Does not match. **Rebuilt as `LVL_StarterVillage_V3`** (phase A, §13), which is the current map; V2 is kept for comparison only. |
| **ADR-017** (village first, surroundings stripped) | **Superseded.** Revision C puts the river, bridges, stream, waterfall and ridge back in the plan, and V3 builds them. |

---

## 15. How to change the layout

1. Edit `Data/Layout/city_layout.csv`. Every row is one primitive: `extent`, `district`, `wall`, `wall_low`, `tower`, `gate`, `bridge`, `street`, `block`, `plaza`, `prop`, `landmark`, `water`, `field`, `ridge`, `ground`, `anchor`, `view`, `label`.
2. Run `python Tools/Layout/build_city_plan.py`.
3. **Fix every conflict it prints.** A block outside the wall, two blocks overlapping, or a street through a block is a data error, not a drawing quirk. (The slums are the one district allowed outside the wall, and the check knows it.)
4. Commit the CSV and both drawings together.

What the check does **not** cover: sightlines, navmesh reachability, terrain slopes, and whether the result looks good. Those need the editor captures in §11.

---

## 16. The owner's decisions (asked 2026-11-15, answered the same day)

| Question | Answer | What changed |
|---|---|---|
| Is 300 × 200 the map or the town? | **The town alone** | Walled town 300 × 200 m; map grows to 420 × 330 m. Revision C. |
| Kerb height? | **12 cm** | 45 cm stone × 12 cm high, 1.5 m zone. ADR-021 closed. |
| Where do the slums go? | **Outside the wall** | 61 buildings on the flood plain, Y −126…−100, either side of the south approach, behind the river. |
| The north gate? | *"what?"* — see below | Gate stays at X 70; §16 explains why in plain words. |
| How many buildings? | **~300** | Exactly 300 street buildings in 37 rows, plus ~10 sheds. |

**The north gate, in plain words.** The cathedral is 30 m wide and 50 m long, and its east end is built *into* the north wall: the wall and the back of the cathedral are the same place, from X −15 to +15. A gate at the middle of the north wall (X 0) would open straight into the back of the cathedral, so there cannot be one there. The only stretch of north wall left is to the east, past the cathedral's precinct and the canonry — and a gate at **X 70** lands between the canonry (which ends at X 44) and the auction forecourt's wall (which starts at X 52, with its gate at X 64–76). So the north gate is off-centre by design: the town's north–south *axis* is the ceremonial approach from the square to the cathedral door, and it stays unbroken. The alternative — a symmetric gate — means demolishing the cathedral's east end, which is the single silhouette the whole town is built around.

**Open:** none blocking. Two things to decide at sign-off: whether the slum suburb wants a wooden bridge of its own to the west fields (it currently has one road out), and whether the windmill stays as an anchor-only landmark or gets a footprint in phase E.

**Handover I could not do:** the concept image needs saving as `Art/Reference/REF_CityOverview_Aerial_01.png`; the level rebuild was done as `LVL_StarterVillage_V3` (§13); `LVL_StarterVillage_V2.umap` is untouched.
