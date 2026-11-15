# Art Direction — Starting Village

Status: **Proposed** — needs the owner's sign-off (ADR-019).
Reference: owner-supplied concept image, 2026-11-15. Save it as `Art/Reference/REF_StarterVillage_MarketSquare_01.png` so every later judgement can be compared against it.
Related: ADR-014 (five districts), ADR-015 (streets and ground), ADR-016 (massing variety), `ART_PIPELINE.md`.

## The look in one sentence

**A painterly late-medieval market town in high autumn: warm ochre plaster on dark oak framing, terracotta roofs, cold blue sky — with one Gothic stone landmark breaking the roofline.**

Grounded rather than cartoony: shapes are simple and chunky (buildable by one artist), but proportions, materials and lighting are believable. Think "stylised realism", not low-poly toy and not photoreal.

## Why the reference works — the five things to protect

1. **Density.** Buildings touch and overlap; every gap is a street or an alley. Nothing stands alone.
2. **A height ladder.** Roofline rises from street edge → civic buildings → cathedral spire. The eye always has somewhere to climb.
3. **Two-material contrast at every scale.** Warm plaster against near-black timber; pale stone against red tile. No surface is a single flat colour.
4. **Warm/cool split.** Warm buildings and warm sunlight sit against a cool blue sky and cool shadows. That split is what makes it read as "morning in a real place".
5. **One landmark.** The cathedral is the only thing allowed to be taller, paler and more detailed than the town around it. It earns its silhouette by contrast, not by size.

## Palette

Sampled by eye from the reference. Canonical values live in `Tools/Blender/palette.json`; if these two disagree, the JSON wins.

| Role | Hex | Material | Used for |
|---|---|---|---|
| Warm infill | `#C9A87C` | `T_Plaster_Warm` | Most half-timbered panels, trade district, townhouses |
| Cream infill | `#E2D5BC` | `T_Plaster_Cream` | Second plaster layer, civic walls, upper storeys |
| Oak framing | `#4B3626` | `T_Timber_Oak` | Beams, posts, braces, lintels, balconies |
| Smoked timber | `#2E2319` | (tint of oak) | Slums, undersides of jetties, beams near forges |
| Clay tile | `#94412F` | `T_Roof_Tile` | Every domestic roof; the town's colour signature |
| Old tile | `#6E4A46` | (tint of tile) | Library, church roof, patched slum roofs |
| Cobble | `#8B8577` | `T_Cobble` | Plaza paving, streets, courtyards |
| Dressed stone | `#B7B1A3` | `T_Stone_Dressed` | Cathedral, town hall, gate towers, plinths, kerbs |
| Iron | `#3A3A3C` | metal 1.0 / rough 0.5 | Hinges, brackets, sign irons, weapon racks, lantern frames |
| Banner red | `#A62B2B` | cloth, rough 0.85 | Hanging banners on poles and facades |
| Banner gold | `#C9A227` | cloth/trim, rough 0.6 | Banner emblem only — no lettering |
| Canvas cream | `#CFC0A4` | cloth, rough 0.9 | Market awnings |
| Canvas red | `#A64B3C` | cloth, rough 0.9 | Striped awnings, stall canopies |
| Lit glass | `#F2B45E` | emissive, weak | Windows lit from inside; forge glow |
| Autumn rust | `#B2452A` | foliage | Tree canopies, fallen leaves on cobble |
| Autumn amber | `#D2803A` | foliage | Tree canopies, hanging foliage over streets |
| Deep autumn | `#6E2B1D` | foliage | Underside of canopy, distant tree masses |
| Kerb moss | `#6E7A4E` | foliage/ground blend | Base of walls, kerb edges, fountain basin |
| Sky | `#74A9DE` | — | Lighting/environment only, never a texture |

Discipline: **red is reserved.** Banners, awnings and the forge are the only saturated reds/oranges in the town. If everything is warm, nothing reads as warm.

## Material set (what gets authored)

Six tileable material families plus accents. Each family is one trim sheet (see `ART_PIPELINE.md` for resolution and texel density).

| Family | Composition | Notes |
|---|---|---|
| `M_Plaster_Warm` | Flat ochre base + low-frequency blotching + fine grain + grime gradient near ground | Two tint variants are material instances, not new textures |
| `M_Plaster_Cream` | Same generator, lighter base | Town hall and upper storeys |
| `M_Timber_Oak` | Dark base + stretched grain + knots + end-grain darkening | One trim sheet covers beam, post, brace, plank |
| `M_Roof_Tile` | Clay tile courses, per-tile hue jitter, slight course sag | The single most repeated surface in the town — read it at 50 m first |
| `M_Cobble` | Irregular stones, mortar gaps, polished wheel tracks, leaf litter decals on top | Plaza and streets share one sheet |
| `M_Stone_Dressed` | Ashlar courses, chisel noise, weathering streaks below sills | Cathedral, civic, plinths, kerbs |

Rules that keep it cheap:

- **One sheet per family.** Variation comes from UV choice, vertex/instance tint, and decals — not from a seventh texture.
- **No baked lighting in base colour.** Sun and shadow come from the level. Baked shadows were the reference's biggest cheat and cannot be re-lit in game.
- **Roughness tells the story, not colour.** Plaster 0.85, timber 0.70, tile 0.62, cobble 0.80, stone 0.78, cloth 0.85–0.90, iron 0.50.
- **Wet and warm only where the story says so:** cobble in the plaza after rain, glow at the forge and in windows. A uniformly glossy town looks like plastic.

## Shape language

| Feature | Rule | Why |
|---|---|---|
| Storey height | 320 cm typical, 280 cm in the slums | Matches ADR-016 massing heights |
| Bay width | 200 cm module, buildings are whole bays (620–1400 cm ⇒ 3–7 bays) | Lets one wall piece serve every building |
| Jetty | Upper storey overhangs 30–40 cm on the street face | The single strongest medieval read; cheap to build |
| Roof pitch | 50° on domestic roofs, 60° on church and towers | Steep enough to dominate the silhouette |
| Timber frame | 20×20 cm members, visible on every plastered facade | Contrast at mid distance; geometry, not texture only |
| Eaves | Overhang 40 cm with visible rafters | Dark line under every roof edge — reads as depth |
| Windows | Small, deep-set, leaded, irregular spacing; shutters on domestic | The reference's windows are glass slits, not glass walls |
| Chimneys | One per building, offset, stone or plastered stack | Vertical accents between the gables |
| Doorways | 100×210 cm, arched on civic, squared with timber lintel on domestic | Cheap variety from one opening kit |
| Gothic detail | Pointed arches, buttresses, pinnacles and one rose window — cathedral only | Landmark language stays exclusive to the landmark |

## District material sets

The districts in ADR-014 must be readable **before** materials (silhouette first). Materials then reinforce them:

| District | Plaster | Roof | Timber | Signature props |
|---|---|---|---|---|
| **Town Hall** | Cream, clean | Old tile, steep | Oak, carved brackets | Banners, lamps, ceremonial steps, glass |
| **Trade District** | Warm ochre, mixed | Clay tile, mixed ages | Oak, some painted | Awnings, signboards, barrels, crates, hand cart |
| **Auction House** | Cream + dressed stone | Dome (metal/lead) | Dark oak | The only metalwork in town: railings, lanterns, strongbox |
| **The Slums** | Patchy cream over older warm, stained | Patched, mismatched, one repaired with planks | Smoked, unpainted | Lean-tos, laundry, scavenged boards, no awnings |
| **Library** | Cream + stone plinth | Old dark tile | Dark oak | Buttresses, tall windows, quiet courtyard |
| **Parish church** | Dressed stone | Old tile | — | Rose window, pinnacles, spire, bell |

Contrast is the point: the slums are the only district where materials are *worn* rather than merely old, and the auction house the only one with polished metal.

## Light and atmosphere

- **Key light:** warm sun (`#FFD9A8`) low in the sky, from the upper left, roughly 25–35° elevation — long shadows, lit stone, shadowed under-eaves.
- **Fill:** cool sky bounce (`#74A9DE`), strong. Shadows should be blue-grey, never black.
- **Practical lights:** lit windows, lanterns on posts, forge fire (`#FF9A3C`). These are the only saturated light sources and the only reason a facade needs an emissive channel.
- **Air:** light haze toward the mountains so distance reads; no fog in the streets.
- **Sky:** deep blue zenith to pale horizon with flat, brushy clouds. Never a gradient texture on a building.
- **Season:** high autumn. Fallen leaves on cobble, amber canopies overhead, a few bare branches. Snow only on distant peaks.

## Do not

- Photoreal pores, scratches and smudge noise everywhere — it reads as generic asset-store, not as this town.
- Lettering on signs or banners. The banners carry a simple geometric mark; readable text needs invented language and is a later decision.
- Colour-coded districts (a "green district", a "blue district"). Districts differ by material condition, height and density.
- More than one hero landmark competing for the skyline.
- Any surface that is one flat colour with no roughness variation.

## Open questions for the owner

1. **How far stylised?** This document assumes grounded-but-painterly. Pushing to flat-shaded low-poly would roughly halve the modelling time and lose the reference's warmth.
2. **Trim sheets vs. unique facades** — accepted as the default (see `ART_PIPELINE.md`); say now if you want unique hero facades on plaza-facing buildings.
3. **Banner sigil.** A neutral mark (chevron/diamond) until the town, faction and god names land in `DESIGN.md`.
4. **How much foliage?** Autumn trees are the largest texture budget item after architecture; 3 canopy variants is the proposed cap.
