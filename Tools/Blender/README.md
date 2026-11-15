# Tools/Blender

Helper scripts for the art pipeline. Nothing here ships with the game or runs at runtime.

## `generate_textures.py`

Writes the six base material sheets from `Docs/ART_DIRECTION.md` as tileable PBR maps — `_BaseColor`, `_Roughness`, `_Normal`, `_Height` — plus `preview_materials.png`.

```
python Tools/Blender/generate_textures.py
python Tools/Blender/generate_textures.py --only T_Roof_Tile --size 2048
python Tools/Blender/generate_textures.py --out Art/Exports/Textures --seed 7
```

Inside Blender, same script:

```
"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" \
  --background --python Tools/Blender/generate_textures.py
```

- Needs only **numpy**; system Python 3.12 and Blender's bundled Python both work.
- Output: `Art/Exports/Textures/<T_Name>/`. That folder is **gitignored** — a fresh clone runs this script once instead of pulling the binaries.
- **`palette.json` is the look.** Colours, roughness and tiling live there; edit it and re-run instead of touching the script.
- Deterministic: each material's noise seed is derived from its name plus `--seed`, so the same command reproduces the same sheets.
- Tiling is by construction — every noise layer wraps on the texture border, which is why the seams are clean and why there is no "seam fix" step later.
- Maps are **not** ORM-packed yet; see `Docs/ART_PIPELINE.md` §4.

Blender on this machine is the **Steam** build at
`C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe` (5.3.0). It is not on `PATH`.
