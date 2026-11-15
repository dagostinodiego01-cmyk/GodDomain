# Art/Blender — source files

`.blend` files are the source of truth for anything modelled. The game never loads them; it loads the exports.

| Rule | Value |
|---|---|
| Units | Metric, 1 unit = 1 m — see `Docs/ART_PIPELINE.md` §1 |
| One file per kit | `VillageFacadeKit.blend`, `StreetKit.blend`, `CivicKit.blend`, `LandscapeKit.blend` |
| Export | `Art/Exports/<Kit>/SM_<Name>.fbx`, transforms applied, one mesh per file |
| Textures | referenced from `Art/Exports/Textures/` (generated) — do not pack copies in here |
| Before an agent session | commit, or save a versioned copy (`Docs/MCP_SETUP.md` warns why) |

Keeping textures external and generated is deliberate: a palette change then reaches every kit piece on the next import, instead of being frozen inside a dozen `.blend` files.
