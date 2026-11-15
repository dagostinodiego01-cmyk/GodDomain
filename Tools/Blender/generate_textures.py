#!/usr/bin/env python3
"""Procedural village material sheets for GD.

Generates the six base materials from Docs/ART_DIRECTION.md as tileable PBR
maps (BaseColor / Roughness / Normal / Height) plus a preview contact sheet.
Only numpy is needed, so it runs with plain Python or inside Blender:

    python Tools/Blender/generate_textures.py
    blender --background --python Tools/Blender/generate_textures.py

Colours and recipes live in Tools/Blender/palette.json, not in this file:
restyling the village is a JSON edit and a re-run, not a code change. Each
material's seed is derived from its name, so output is reproducible.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import zlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
PALETTE_PATH = ROOT / "Tools" / "Blender" / "palette.json"
DEFAULT_OUT = ROOT / "Art" / "Exports" / "Textures"


# ---------------------------------------------------------------- noise utils

def _smoothstep(t: np.ndarray) -> np.ndarray:
    return t * t * (3.0 - 2.0 * t)


def value_noise(size: int, period_x: int, period_y: int, rng: np.random.Generator) -> np.ndarray:
    """Tileable value noise: a random grid sampled with smooth interpolation.

    The grid wraps, so anything built from this tiles seamlessly.
    """
    grid = rng.random((period_y, period_x)).astype(np.float32)
    xs = (np.arange(size, dtype=np.float32) + 0.5) * (period_x / size)
    ys = (np.arange(size, dtype=np.float32) + 0.5) * (period_y / size)

    ix = np.floor(xs).astype(np.int64)
    iy = np.floor(ys).astype(np.int64)
    tx = _smoothstep(xs - ix)[None, :]
    ty = _smoothstep(ys - iy)[:, None]

    x0 = ix % period_x
    x1 = (ix + 1) % period_x
    y0 = iy % period_y
    y1 = (iy + 1) % period_y

    a = grid[np.ix_(y0, x0)]
    b = grid[np.ix_(y0, x1)]
    c = grid[np.ix_(y1, x0)]
    d = grid[np.ix_(y1, x1)]

    top = a + (b - a) * tx
    bottom = c + (d - c) * tx
    return (top + (bottom - top) * ty).astype(np.float32)


def fbm(size: int, base: int, octaves: int, rng: np.random.Generator,
        aniso: float = 1.0, gain: float = 0.5) -> np.ndarray:
    """Fractal sum of value noise. `aniso` > 1 stretches features along X."""
    total = np.zeros((size, size), np.float32)
    amplitude = 1.0
    norm = 0.0
    period = float(base)
    for _ in range(octaves):
        px = max(1, int(round(period)))
        py = max(1, int(round(period * aniso)))
        total += amplitude * value_noise(size, px, py, rng)
        norm += amplitude
        amplitude *= gain
        period *= 2.0
    return total / norm


def cell_field(size: int, cells_x: int, cells_y: int, rng: np.random.Generator,
               jitter: float = 0.85) -> tuple[np.ndarray, np.ndarray]:
    """Tileable jittered-grid cells. Returns (distance in uv, cell id)."""
    points = rng.random((cells_y, cells_x, 2)).astype(np.float32)
    points = points * jitter + (1.0 - jitter) * 0.5

    uv = (np.arange(size, dtype=np.float32) + 0.5) / size
    gx = uv[None, :]
    gy = uv[:, None]

    best = np.full((size, size), 1e9, np.float32)
    best_id = np.zeros((size, size), np.int32)

    cell_x = np.floor(gx * cells_x).astype(np.int64)
    cell_y = np.floor(gy * cells_y).astype(np.int64)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ix = cell_x + dx
            iy = cell_y + dy
            wx = ix % cells_x
            wy = iy % cells_y
            # Cell centre in uv; ix/iy stay unwrapped so seam cells measure correctly.
            centre_x = (ix + points[wy, wx, 0]) / cells_x
            centre_y = (iy + points[wy, wx, 1]) / cells_y
            dist = (gx - centre_x) ** 2 + (gy - centre_y) ** 2
            closer = dist < best
            best = np.where(closer, dist, best)
            best_id = np.where(closer, (wy * cells_x + wx).astype(np.int32), best_id)

    return np.sqrt(best).astype(np.float32), best_id


# ------------------------------------------------------------------ patterns

def mat_plaster(size, base, rough, rng):
    """Flat ochre/cream render with blotching, grain and damp staining."""
    blotch = fbm(size, 3, 3, rng)
    grain = fbm(size, 64, 4, rng, gain=0.55)

    height = 0.6 * grain + 0.4 * blotch
    albedo = base[None, None, :] * (0.90 + 0.16 * blotch[..., None])
    albedo = albedo * (0.97 + 0.06 * grain[..., None])

    stain = np.clip((fbm(size, 2, 3, rng) - 0.58) * 3.0, 0.0, 1.0)
    albedo = albedo * (1.0 - 0.16 * stain[..., None])

    roughness = np.clip(rough + (grain - 0.5) * 0.08 - 0.05 * stain, 0.4, 1.0)
    return albedo, roughness, height


def mat_timber(size, base, rough, rng):
    """Oak: horizontal grain (along U), tight rings, knots, sawn surface."""
    band = fbm(size, 4, 4, rng, aniso=10.0, gain=0.55)
    streak = fbm(size, 16, 5, rng, aniso=18.0, gain=0.6)

    v = (np.arange(size, dtype=np.float32) / size)[:, None]
    rings = 0.5 + 0.5 * np.sin(2.0 * np.pi * (v * 13.0 + band * 1.1 + streak * 0.6))
    rings = rings ** 1.6

    height = 0.55 * rings + 0.45 * streak
    albedo = base[None, None, :] * (0.58 + 0.68 * rings[..., None])
    albedo = albedo * (0.94 + 0.12 * streak[..., None])

    knots = np.clip((fbm(size, 2, 2, rng) - 0.76) * 7.0, 0.0, 1.0)
    albedo = albedo * (1.0 - 0.38 * knots[..., None])

    roughness = np.clip(rough + 0.12 * (1.0 - rings), 0.4, 1.0)
    return albedo, roughness, height


def mat_roof(size, base, rough, rng):
    """Clay tile: 8 courses of 8 barrel tiles per 2 m, per-tile hue jitter."""
    rows, cols = 8, 8
    uv = (np.arange(size, dtype=np.float32) + 0.5) / size

    u = uv[None, :] * cols
    v = uv[:, None] * rows
    row = np.floor(v).astype(np.int64)

    shifted = (u + 0.5 * (row % 2)) % cols
    col = np.floor(shifted).astype(np.int64) % cols

    fu = (shifted % 1.0) - 0.5
    fv = (v % 1.0) - 0.5

    tint_table = rng.uniform(0.86, 1.12, (rows, cols)).astype(np.float32)
    tint = tint_table[row, col]

    arch = np.sqrt(np.clip(1.0 - (fu / 0.5) ** 2, 0.0, 1.0))
    lip = 1.0 - np.clip((fv + 0.5) / 0.22, 0.0, 1.0)
    height = arch * (0.50 + 0.50 * lip)

    albedo = base[None, None, :] * tint[..., None] * (0.80 + 0.35 * height[..., None])
    albedo = albedo * (1.0 - 0.45 * (1.0 - arch)[..., None])

    # Weathering at the 2 m scale, so a roof does not read as one flat red sheet.
    soil = np.clip((fbm(size, 2, 3, rng) - 0.52) * 2.2, 0.0, 1.0)
    albedo = albedo * (1.0 - 0.16 * soil[..., None])

    roughness = np.clip(rough + 0.15 * (1.0 - arch) + (tint - 1.0) * 0.15
                        + 0.10 * soil, 0.35, 1.0)
    return albedo, roughness, height


def mat_cobble(size, base, mortar, rough, rng):
    """Setts in mortar: flat worn tops, crisp shoulders, dirt in the joints."""
    cells = 9
    dist, cell_id = cell_field(size, cells, cells, rng, jitter=0.75)
    # Flat worn top, short bevel, thin joints — a wide ramp reads as balls, not setts.
    shoulder = np.clip((0.44 - dist * cells) / 0.12, 0.0, 1.0)

    height = shoulder ** 0.7
    height = np.clip(height + 0.04 * (fbm(size, 96, 3, rng) - 0.5), 0.0, 1.0)

    tint_table = rng.uniform(0.82, 1.16, cells * cells).astype(np.float32)
    tint = tint_table[cell_id]

    mask = np.clip(height / 0.22, 0.0, 1.0)
    stone = base[None, None, :] * tint[..., None] * (0.92 + 0.14 * height[..., None])
    joint = mortar * 0.80
    albedo = joint[None, None, :] + (stone - joint[None, None, :]) * mask[..., None]
    albedo = albedo * (0.88 + 0.12 * mask[..., None])

    polish = np.clip((fbm(size, 2, 3, rng) - 0.62) * 3.0, 0.0, 1.0)
    grime = np.clip((fbm(size, 4, 3, rng) - 0.55) * 2.5, 0.0, 1.0)

    roughness = np.clip(rough + 0.16 * (1.0 - mask) - 0.24 * polish + 0.08 * grime, 0.3, 1.0)
    albedo = albedo * (1.0 - 0.10 * grime[..., None])
    return albedo, roughness, height


def mat_stone(size, base, mortar, rough, rng):
    """Dressed ashlar: 6 courses of 4 blocks, half-block stagger, chisel faces."""
    rows, cols = 6, 4
    uv = (np.arange(size, dtype=np.float32) + 0.5) / size

    v = uv[:, None] * rows
    row = np.floor(v).astype(np.int64)

    u = uv[None, :] * cols + 0.5 * (row % 2)
    col = np.floor(u).astype(np.int64) % cols

    fu = (u % 1.0) - 0.5
    fv = (v % 1.0) - 0.5

    tint_table = rng.uniform(0.90, 1.08, (rows, cols)).astype(np.float32)
    tint = tint_table[row, col]

    edge = np.minimum(0.5 - np.abs(fu), 0.5 - np.abs(fv))
    height = np.clip(edge / 0.055, 0.0, 1.0) ** 0.6

    chisel = fbm(size, 32, 3, rng)
    height = np.clip(height * (0.85 + 0.15 * chisel), 0.0, 1.0)

    face = base[None, None, :] * tint[..., None] * (0.94 + 0.10 * chisel[..., None])
    albedo = mortar[None, None, :] + (face - mortar[None, None, :]) * height[..., None]

    wash = np.clip((fbm(size, 3, 3, rng) - 0.6) * 2.5, 0.0, 1.0)
    albedo = albedo * (1.0 - 0.14 * wash[..., None])

    roughness = np.clip(rough + 0.10 * (1.0 - height) - 0.06 * wash, 0.4, 1.0)
    return albedo, roughness, height


PATTERNS = {
    "plaster": mat_plaster,
    "timber": mat_timber,
    "roof_tile": mat_roof,
    "cobble": mat_cobble,
    "stone_block": mat_stone,
}


# ------------------------------------------------------------------- helpers

def hex_rgb(value: str) -> np.ndarray:
    value = value.lstrip("#")
    return np.array([int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


def normal_from_height(height: np.ndarray, strength: float = 6.0) -> np.ndarray:
    dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 0.5
    dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 0.5

    n = np.dstack([-dx * strength, -dy * strength, np.ones_like(height)]).astype(np.float32)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def to_u8(array: np.ndarray) -> np.ndarray:
    return np.clip(array * 255.0 + 0.5, 0.0, 255.0).astype(np.uint8)


def write_png(path: pathlib.Path, pixels: np.ndarray) -> None:
    """Minimal PNG writer, so the generator needs nothing beyond numpy."""
    pixels = np.ascontiguousarray(pixels)
    height, width = pixels.shape[:2]
    colour_type = 2 if pixels.ndim == 3 else 0

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct_pack(len(data)) + tag + data
                + struct_pack(zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + pixels[y].tobytes() for y in range(height))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct_pack(width) + struct_pack(height) + bytes([8, colour_type, 0, 0, 0]))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    path.write_bytes(png)


def struct_pack(value: int) -> bytes:
    import struct
    return struct.pack(">I", value)


# ---------------------------------------------------------------------- main

def build(spec: dict, name: str, size: int, seed: int):
    pattern = spec["pattern"]
    if pattern not in PATTERNS:
        raise SystemExit(f"{name}: unknown pattern {pattern!r}")

    base = hex_rgb(spec["base"])
    mortar = hex_rgb(spec.get("mortar", "#8a8478"))
    rough = float(spec.get("roughness", 0.8))
    rng = np.random.default_rng((zlib.crc32(name.encode()) + seed) & 0xFFFFFFFF)

    if pattern == "cobble":
        return PATTERNS[pattern](size, base, mortar, rough, rng)
    if pattern == "stone_block":
        return PATTERNS[pattern](size, base, mortar, rough, rng)
    return PATTERNS[pattern](size, base, rough, rng)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate GD village material sheets.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output directory")
    parser.add_argument("--size", type=int, default=None, help="override resolution")
    parser.add_argument("--only", action="append", default=None,
                        help="material name to build (repeatable), e.g. T_Roof_Tile")
    parser.add_argument("--seed", type=int, default=0, help="extra seed offset")
    args = parser.parse_args(argv)

    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    default_size = int(palette.get("units", {}).get("default_size", 1024))
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    wanted = args.only or list(palette["generated"].keys())
    previews = []

    for name in wanted:
        spec = palette["generated"].get(name)
        if spec is None:
            raise SystemExit(f"{name}: not in palette.json")

        started = time.perf_counter()
        size = int(args.size or spec.get("size", default_size))
        albedo, roughness, height = build(spec, name, size, args.seed)
        normal = normal_from_height(height)

        folder = out_dir / name
        folder.mkdir(exist_ok=True)
        write_png(folder / f"{name}_BaseColor.png", to_u8(albedo))
        write_png(folder / f"{name}_Roughness.png", to_u8(np.clip(roughness, 0.0, 1.0)))
        write_png(folder / f"{name}_Normal.png", to_u8(normal))
        write_png(folder / f"{name}_Height.png", to_u8(np.clip(height, 0.0, 1.0)))

        # Quarter scale: a full-size contact sheet is too large to attach and view.
        previews.append(albedo[::4, ::4])
        tiling = spec.get("tiling_m", palette["units"]["texture_tiling_m"])
        print(f"  {name:<20} {size}x{size}  {tiling:g} m tile  "
              f"({size / float(tiling):.0f} px/m)  {time.perf_counter() - started:.1f}s")

    if previews:
        write_png(out_dir / "preview_materials.png", to_u8(np.concatenate(previews, axis=1)))

    print(f"\nWrote {len(previews)} material(s) + preview_materials.png to {out_dir}")
    return 0


if __name__ == "__main__":
    cli = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    raise SystemExit(main(cli))
