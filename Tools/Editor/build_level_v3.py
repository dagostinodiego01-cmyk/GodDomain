#!/usr/bin/env python3
"""Build the starter-city greybox in the editor from Data/Layout/city_layout.csv.

Phase A ("setout") of Docs/CITY_LAYOUT.md. Three rules shape everything here:

  * **One actor per building.** A block row is not one box: it is `count` separate
    buildings in a regular array, so each can be swapped for a model later without
    touching its neighbours.
  * **The ground has a river in it.** The ground is cut along the river and the
    stream, with a bed under each channel and the water surface below the bank, so
    the water and the bridges are real geometry rather than markers.
  * **Colour is part of the setout.** Each category uses a duplicated cube/
    cylinder/sphere with its own material instance, so ground, water, stone,
    plaster, slums and paving are distinguishable at a glance.

It spawns through the editor's MCP server (Docs/MCP_SETUP.md) and batches every
actor through one `execute_tool_script` call — 500 actors in seconds instead of
minutes of round trips. The .umap is written by the editor, never by this script.

    python Tools/Editor/build_level_v3.py                 # dry run
    python Tools/Editor/build_level_v3.py --apply --clear # rebuild the level
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "Tools" / "Layout"))

import build_city_plan as plan  # noqa: E402

MESH_ROOT = "/Game/StarterVillage/Greybox/Meshes"
MESH = {
    "ground": f"{MESH_ROOT}/SM_Ground.SM_Ground",
    "ridge": f"{MESH_ROOT}/SM_Ridge.SM_Ridge",
    "town": f"{MESH_ROOT}/SM_Town.SM_Town",
    "slum": f"{MESH_ROOT}/SM_Slum.SM_Slum",
    "stone": f"{MESH_ROOT}/SM_Stone.SM_Stone",
    "pave": f"{MESH_ROOT}/SM_Pave.SM_Pave",
    "water": f"{MESH_ROOT}/SM_Water.SM_Water",
    "landmark": f"{MESH_ROOT}/SM_Landmark.SM_Landmark",
    "water_cyl": f"{MESH_ROOT}/SM_WaterCyl.SM_WaterCyl",
    "dome": f"{MESH_ROOT}/SM_Dome.SM_Dome",
}
FOLDER = "GD/Greybox"

MAP_X = 210.0                # the playable map is 420 x 330; the ground stops there
MAP_Y = 165.0
GROUND_Z = (-2.0, 0.0)
PAVE = (0.02, 0.12)
GATE_PASS = 8.0
DECK = 1.2                   # bridge deck above the bank, so it reads as a bridge

HEIGHT_BAND = {
    "Trade": (9.0, 16.0),
    "Civic": (9.0, 14.0),
    "Auction House": (10.0, 15.0),
    "Library": (7.0, 12.0),
    "The Slums": (3.5, 7.0),
}

GATE_OPENING = {"G_S": 8.0, "G_W": 6.0, "G_E": 6.0, "G_N": 8.0,
                "G_P": 4.0, "G_FORE": 6.0}


class Box:
    __slots__ = ("label", "folder", "cx", "cy", "z0", "z1", "sx", "sy", "yaw", "mesh")

    def __init__(self, label, folder, cx, cy, z0, z1, sx, sy, yaw=0.0, mesh=None):
        self.label = label
        self.folder = folder
        self.cx, self.cy = cx, cy
        self.z0, self.z1 = z0, z1
        self.sx, self.sy = sx, sy
        self.yaw = yaw
        self.mesh = mesh or MESH["stone"]

    def as_args(self) -> dict:
        return {
            "asset_path": self.mesh,
            "name": self.label,
            "xform": {
                "location": {"x": self.cx * 100, "y": self.cy * 100,
                             "z": (self.z0 + self.z1) * 50},
                "rotation": {"pitch": 0.0, "yaw": self.yaw, "roll": 0.0},
                "scale": {"x": self.sx, "y": self.sy, "z": self.z1 - self.z0},
            },
            "folder": self.folder,
        }


# ------------------------------------------------------------------ helpers
def y_at(pts, x: float) -> float:
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        if min(x1, x2) <= x <= max(x1, x2):
            if abs(x2 - x1) < 1e-6:
                return y1
            return y1 + (x - x1) / (x2 - x1) * (y2 - y1)
    return pts[-1][1] if x > pts[-1][0] else pts[0][1]


def seg_boxes(label, folder, pts, width, z0, z1, mesh):
    out = []
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length < 0.01:
            continue
        out.append(Box(f"{label}{i}", folder, (x1 + x2) / 2, (y1 + y2) / 2,
                       z0, z1, length, width, math.degrees(math.atan2(dy, dx)), mesh))
    return out


def masked_seg_boxes(label, folder, pts, width, z0, z1, gates, mesh):
    out = []
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length < 0.01:
            continue
        ux, uy = dx / length, dy / length
        yaw = math.degrees(math.atan2(dy, dx))
        gaps = []
        for gx, gy, sx, sy in gates:
            rx, ry = gx - x1, gy - y1
            t = rx * ux + ry * uy
            perp = abs(-rx * uy + ry * ux)
            if perp > width / 2 + 3.0:
                continue
            half = abs(ux) * sx / 2 + abs(uy) * sy / 2
            a, b = max(0.0, t - half), min(length, t + half)
            if b > a:
                gaps.append((a, b))
        gaps.sort()
        cursor, runs = 0.0, []
        for a, b in gaps:
            if a > cursor + 0.05:
                runs.append((cursor, a))
            cursor = max(cursor, b)
        if cursor < length - 0.05:
            runs.append((cursor, length))
        for j, (a, b) in enumerate(runs):
            mid = (a + b) / 2
            out.append(Box(f"{label}_{i}{chr(97 + j)}", folder,
                           x1 + ux * mid, y1 + uy * mid, z0, z1, b - a, width, yaw, mesh))
    return out


def clip_to_water(pts, river_pts, river_half, stream_lo, stream_hi):
    """Drop the parts of a path that would float over a water channel.

    Paving pads are 10 cm slabs; left whole they bridge the river at ground level
    and the bridge, the banks and the water all disappear behind a flat lid.
    """
    runs, current = [], []
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        length = math.hypot(x2 - x1, y2 - y1)
        steps = max(1, int(length))
        for s in range(steps):
            t = s / steps
            x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            wet = abs(y - y_at(river_pts, x)) < river_half + 1.0
            if stream_lo is not None and stream_lo - 1.0 < x < stream_hi + 1.0 and -150 < y < 100:
                wet = True
            if wet:
                if len(current) >= 2:
                    runs.append((current[0], current[-1]))
                current = []
            else:
                current.append((x, y))
        if len(current) >= 2:
            runs.append((current[0], current[-1]))
            current = []
    if len(current) >= 2:
        runs.append((current[0], current[-1]))
    return runs


def house_height(district: str, i: int, j: int) -> float:
    lo, hi = HEIGHT_BAND.get(district, (8.0, 12.0))
    t = ((i * 37 + j * 61) % 100) / 100.0
    return round(lo + (hi - lo) * t, 1)


# ------------------------------------------------------------------- build
def ground_and_water(rows) -> list[Box]:
    out: list[Box] = []
    folder = f"{FOLDER}/Ground"
    river = next(w for w in plan.by_type(rows, "water") if w["id"] == "RIVER")
    pts = river["shape"][1]
    half = (plan.num(river, "width_m") or 16) / 2
    stream = next((w for w in plan.by_type(rows, "water") if w["id"] == "STREAM"), None)
    s_lo, s_hi = (164.0, 174.0) if stream else (None, None)

    slices = 14
    width = (2 * MAP_X) / slices
    for i in range(slices):
        xa = -MAP_X + i * width
        xb = xa + width
        ym = y_at(pts, (xa + xb) / 2)
        y_n, y_s = ym + half, ym - half
        pieces = [(xa, xb)]
        if s_lo is not None and xa < s_hi and xb > s_lo:
            pieces = [(xa, s_lo), (s_hi, xb)]
        for k, (pa, pb) in enumerate(pieces):
            if pb - pa < 0.5:
                continue
            out.append(Box(f"GROUND_N{i}{k}", folder, (pa + pb) / 2, (y_n + MAP_Y) / 2,
                           GROUND_Z[0], GROUND_Z[1], pb - pa, MAP_Y - y_n, mesh=MESH["ground"]))
            out.append(Box(f"GROUND_S{i}{k}", folder, (pa + pb) / 2, (-MAP_Y + y_s) / 2,
                           GROUND_Z[0], GROUND_Z[1], pb - pa, y_s + MAP_Y, mesh=MESH["ground"]))
        out.append(Box(f"RIVERBED{i}", f"{FOLDER}/Water", (xa + xb) / 2, ym, -6.0, -5.6,
                       width, half * 2 + 2, mesh=MESH["water"]))

    if s_lo is not None:
        cx = (s_lo + s_hi) / 2
        out.append(Box("STREAMBED", f"{FOLDER}/Water", cx, (-146 + 100) / 2,
                       -2.2, -2.0, s_hi - s_lo, 246, mesh=MESH["water"]))
        out.append(Box("STREAM", f"{FOLDER}/Water", cx, (-146 + 86) / 2,
                       -1.05, -1.0, s_hi - s_lo, 232, mesh=MESH["water"]))

    out += seg_boxes("RIVER", f"{FOLDER}/Water", pts, half * 2, -4.55, -4.5, MESH["water"])
    return out


def terrain() -> list[Box]:
    """The ridge in the north-east: two terraces with the waterfall on their face."""
    return [
        Box("RIDGE_LOW", f"{FOLDER}/Ground", 178.0, 138.0, 0.0, 22.0, 64.0, 70.0,
            mesh=MESH["ridge"]),
        Box("RIDGE_HIGH", f"{FOLDER}/Ground", 184.0, 152.0, 22.0, 30.0, 52.0, 42.0,
            mesh=MESH["ridge"]),
    ]


def fall_and_pool(rows) -> list[Box]:
    out = []
    fall = next((w for w in plan.by_type(rows, "water") if w["id"] == "FALL"), None)
    if fall:
        x1, y1, x2, y2 = plan.shape_bbox(fall["shape"])
        out.append(Box("FALL", f"{FOLDER}/Water", (x1 + x2) / 2, (y1 + y2) / 2,
                       -1.0, 22.0, x2 - x1, y2 - y1, mesh=MESH["water"]))
    pool = next((w for w in plan.by_type(rows, "water") if w["id"] == "POOL"), None)
    if pool:
        cx, cy, r = pool["shape"][1]
        out.append(Box("POOL", f"{FOLDER}/Water", cx, cy, -1.05, -1.0,
                       r * 1.8, r * 1.8, mesh=MESH["water_cyl"]))
    return out


def buildings(rows) -> list[Box]:
    out: list[Box] = []
    for b in plan.by_type(rows, "block"):
        x1, y1, x2, y2 = plan.shape_bbox(b["shape"])
        n = max(1, int(plan.num(b, "count") or 1))
        along_x = (x2 - x1) >= (y2 - y1)
        length = (x2 - x1) if along_x else (y2 - y1)
        depth = (y2 - y1) if along_x else (x2 - x1)
        stacks = 2 if depth >= 17.0 else 1
        # The block's `count` is the number of buildings it holds, so share it out
        # exactly across the rows instead of rounding per row — otherwise a block
        # of 13 back-to-back plots comes out as 12 and the district total drifts
        # away from the plan's 300.
        base, rem = divmod(n, stacks)
        per_row = [base + (1 if r < rem else 0) for r in range(stacks)]
        step = depth / stacks
        gap = 0.4
        mesh = MESH["slum"] if b["district"] == "The Slums" else MESH["town"]
        folder = f"{FOLDER}/Buildings/{b['district'].replace(' ', '')}"
        for r in range(stacks):
            count = max(1, per_row[r])
            slice_w = length / count
            for i in range(count):
                if along_x:
                    cx = x1 + slice_w * (i + 0.5)
                    cy = y1 + step * (r + 0.5)
                    sx, sy = slice_w - gap, step - gap
                else:
                    cx = x1 + step * (r + 0.5)
                    cy = y1 + slice_w * (i + 0.5)
                    sx, sy = step - gap, slice_w - gap
                h = house_height(b["district"], i, r)
                out.append(Box(f"{b['id']}_{r}{i:02d}", folder, cx, cy, 0.0, h, sx, sy,
                               mesh=mesh))
    return out


def bridges(rows) -> list[Box]:
    """Deck above the bank, stepped approaches, parapets and piers."""
    out: list[Box] = []
    folder = f"{FOLDER}/Bridges"
    for b in plan.by_type(rows, "bridge"):
        x1, y1, x2, y2 = plan.shape_bbox(b["shape"])
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        span_x = (x2 - x1) >= (y2 - y1)
        long_m = (x2 - x1) if span_x else (y2 - y1)
        wide_m = (y2 - y1) if span_x else (x2 - x1)
        ramp = 3.6
        body = long_m - 2 * ramp
        out.append(Box(f"{b['id']}_DECK", folder, cx, cy, -0.8, DECK,
                       body if span_x else wide_m, wide_m if span_x else body))
        # Stepped approach at each end, outside the deck: three 0.4 m rises from
        # the bank up to the deck, so the bridge has a legible profile from the
        # road and the character can walk up it without a ramp mesh.
        for s in (-1, 1):
            for k in range(3):
                off = body / 2 + (ramp / 3) * (k + 0.5)
                z = DECK - k * (DECK / 3)
                if span_x:
                    out.append(Box(f"{b['id']}_STEP{s}{k}", folder, cx + s * off, cy,
                                   -0.8, z, ramp / 3, wide_m))
                else:
                    out.append(Box(f"{b['id']}_STEP{s}{k}", folder, cx, cy + s * off,
                                   -0.8, z, wide_m, ramp / 3))
        for s in (-1, 1):
            if span_x:
                out.append(Box(f"{b['id']}_PARA{s}", folder, cx, cy + s * (wide_m / 2 - 0.3),
                               DECK, DECK + 1.2, body, 0.6))
            else:
                out.append(Box(f"{b['id']}_PARA{s}", folder, cx + s * (wide_m / 2 - 0.3), cy,
                               0.0, DECK + 1.2, 0.6, body))
        for s in (-1, 1):
            off = long_m * 0.28
            if span_x:
                out.append(Box(f"{b['id']}_PIER{s}", folder, cx + s * off, cy, -6.0, -0.8,
                               wide_m * 0.55, wide_m * 0.8))
            else:
                out.append(Box(f"{b['id']}_PIER{s}", folder, cx, cy + s * off, -6.0, -0.8,
                               wide_m * 0.8, wide_m * 0.55))
    return out


def build(rows) -> list[Box]:
    boxes: list[Box] = []
    folder = FOLDER
    boxes += ground_and_water(rows)
    boxes += terrain()
    boxes += fall_and_pool(rows)

    gate_rects = []
    for g in plan.by_type(rows, "gate"):
        gx1, gy1, gx2, gy2 = plan.shape_bbox(g["shape"])
        gate_rects.append(((gx1 + gx2) / 2, (gy1 + gy2) / 2, gx2 - gx1, gy2 - gy1))

    for w in plan.by_type(rows, "wall"):
        boxes += masked_seg_boxes(w["id"], f"{folder}/Wall", w["shape"][1],
                                  plan.num(w, "width_m") or 1.8, 0.0,
                                  plan.num(w, "height_m") or 10, gate_rects, MESH["stone"])
    for w in plan.by_type(rows, "wall_low"):
        boxes += masked_seg_boxes(w["id"], f"{folder}/Wall", w["shape"][1],
                                  plan.num(w, "width_m") or 1.0, 0.0,
                                  plan.num(w, "height_m") or 6, gate_rects, MESH["stone"])

    for t in plan.by_type(rows, "tower"):
        x1, y1, x2, y2 = plan.shape_bbox(t["shape"])
        h = plan.num(t, "height_m") or 14
        boxes.append(Box(t["id"], f"{folder}/Wall", (x1 + x2) / 2, (y1 + y2) / 2, 0.0, h,
                         x2 - x1, y2 - y1, mesh=MESH["stone"]))
        boxes.append(Box(f"{t['id']}_CAP", f"{folder}/Wall", (x1 + x2) / 2, (y1 + y2) / 2,
                         h, h + 1.6, (x2 - x1) + 1.2, (y2 - y1) + 1.2, mesh=MESH["stone"]))

    for g in plan.by_type(rows, "gate"):
        x1, y1, x2, y2 = plan.shape_bbox(g["shape"])
        h = plan.num(g, "height_m") or 12
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        opening = GATE_OPENING.get(g["id"], 0.0)
        along_x = (x2 - x1) >= (y2 - y1)
        span = (x2 - x1) if along_x else (y2 - y1)
        if not opening or opening >= span - 1.5:
            boxes.append(Box(g["id"], f"{folder}/Gates", cx, cy, 0.0, h, x2 - x1, y2 - y1,
                             mesh=MESH["stone"]))
            continue
        half = opening / 2
        pass_h = min(h - 4.0, GATE_PASS)
        if along_x:
            boxes.append(Box(f"{g['id']}_W", f"{folder}/Gates", (x1 + cx - half) / 2, cy,
                             0.0, h, (cx - half) - x1, y2 - y1, mesh=MESH["stone"]))
            boxes.append(Box(f"{g['id']}_E", f"{folder}/Gates", (cx + half + x2) / 2, cy,
                             0.0, h, x2 - (cx + half), y2 - y1, mesh=MESH["stone"]))
            boxes.append(Box(f"{g['id']}_LINTEL", f"{folder}/Gates", cx, cy, pass_h, h,
                             opening, y2 - y1, mesh=MESH["stone"]))
        else:
            boxes.append(Box(f"{g['id']}_S", f"{folder}/Gates", cx, (y1 + cy - half) / 2,
                             0.0, h, x2 - x1, (cy - half) - y1, mesh=MESH["stone"]))
            boxes.append(Box(f"{g['id']}_N", f"{folder}/Gates", cx, (cy + half + y2) / 2,
                             0.0, h, x2 - x1, y2 - (cy + half), mesh=MESH["stone"]))
            boxes.append(Box(f"{g['id']}_LINTEL", f"{folder}/Gates", cx, cy, pass_h, h,
                             x2 - x1, opening, mesh=MESH["stone"]))

    boxes += bridges(rows)

    river = next(w for w in plan.by_type(rows, "water") if w["id"] == "RIVER")
    river_pts = river["shape"][1]
    river_half = (plan.num(river, "width_m") or 16) / 2
    has_stream = any(w["id"] == "STREAM" for w in plan.by_type(rows, "water"))
    for s in plan.by_type(rows, "street"):
        for run in clip_to_water(s["shape"][1], river_pts, river_half,
                                 164.0 if has_stream else None,
                                 174.0 if has_stream else None):
            boxes += seg_boxes(s["id"], f"{folder}/Streets", run,
                               plan.num(s, "width_m") or 5, PAVE[0], PAVE[1], MESH["pave"])

    for p in plan.by_type(rows, "plaza"):
        x1, y1, x2, y2 = plan.shape_bbox(p["shape"])
        boxes.append(Box(p["id"], f"{folder}/Plazas", (x1 + x2) / 2, (y1 + y2) / 2,
                         PAVE[0], PAVE[1], x2 - x1, y2 - y1, mesh=MESH["pave"]))

    boxes += buildings(rows)

    for lm in plan.by_type(rows, "landmark"):
        kind, p = lm["shape"]
        h = plan.num(lm, "height_m") or 8
        z0 = 0.0
        if lm["id"] == "L_CATH_FLECHE":
            z0, h = 26.0, 58.0
        elif lm["id"] == "L_LIB_YARD":
            continue
        if lm["id"] == "L_AUC":
            cx, cy, r = p
            boxes.append(Box("L_AUC_DRUM", f"{folder}/Landmarks", cx, cy, 0.0, 22.0,
                             r * 2, r * 2, mesh=MESH["landmark"]))
            boxes.append(Box("L_AUC_DOME", f"{folder}/Landmarks", cx, cy, 22.0, 22.0 + r,
                             r * 2 * 0.98, r * 2 * 0.98, mesh=MESH["dome"]))
            continue
        if kind == "circle":
            cx, cy, r = p
            boxes.append(Box(lm["id"], f"{folder}/Landmarks", cx, cy, z0, h,
                             r * 1.8, r * 1.8, mesh=MESH["landmark"]))
        else:
            x1, y1, x2, y2 = p
            boxes.append(Box(lm["id"], f"{folder}/Landmarks", (x1 + x2) / 2, (y1 + y2) / 2,
                             z0, h, x2 - x1, y2 - y1, mesh=MESH["landmark"]))

    for w in plan.by_type(rows, "water"):
        if w["id"] in ("RIVER", "STREAM", "FALL", "POOL"):
            continue
        if w["shape"][0] == "line":
            boxes += seg_boxes(w["id"], f"{folder}/Water", w["shape"][1],
                               plan.num(w, "width_m") or 8, -1.05, -1.0, MESH["water"])
        else:
            x1, y1, x2, y2 = plan.shape_bbox(w["shape"])
            boxes.append(Box(w["id"], f"{folder}/Water", (x1 + x2) / 2, (y1 + y2) / 2,
                             -1.05, -1.0, x2 - x1, y2 - y1, mesh=MESH["water"]))

    for p in plan.by_type(rows, "prop"):
        kind, geom = p["shape"]
        if kind == "circle":
            cx, cy, r = geom
            h = plan.num(p, "height_m") or 3
            boxes.append(Box(p["id"], f"{folder}/Props", cx, cy, 0.0, h,
                             r * 1.8, r * 1.8, mesh=MESH["stone"]))
        else:
            x1, y1, x2, y2 = geom
            boxes.append(Box(p["id"], f"{folder}/Props", (x1 + x2) / 2, (y1 + y2) / 2,
                             0.0, 2.4, x2 - x1, y2 - y1, mesh=MESH["stone"]))
    return boxes


# -------------------------------------------------------------------- apply
SPAWN_SCRIPT = '''
import json

def call(name, args):
    return execute_tool(name, json.dumps(args))

def run():
    items = json.loads(ITEMS)
    made, failed = 0, []
    for it in items:
        try:
            ref = call("editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset",
                       {"asset_path": it["asset_path"], "name": it["name"],
                        "xform": it["xform"]})["returnValue"]
        except Exception as e:
            failed.append(it["name"] + ": " + str(e)[:70])
            continue
        made += 1
        try:
            call("editor_toolset.toolsets.scene.SceneTools.set_actor_folder",
                 {"actor": ref, "folder_path": it["folder"]})
        except Exception as e:
            failed.append(it["name"] + " folder: " + str(e)[:50])
    return {"made": made, "total": len(items), "failed": failed[:10]}
'''

CLEAR_SCRIPT = '''
import json

def call(name, args):
    return execute_tool(name, json.dumps(args))

def run():
    refs = call("editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder",
                {"folder_path": FOLDER, "recursive": True})["returnValue"] or []
    removed, failed = 0, []
    for r in refs:
        try:
            call("editor_toolset.toolsets.scene.SceneTools.remove_from_scene", {"actor": r})
            removed += 1
        except Exception as e:
            failed.append(str(e)[:50])
    return {"removed": removed, "failed": failed[:5]}
'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--level", default="/Game/StarterVillage/LVL_StarterVillage_V3")
    args = ap.parse_args(argv)

    boxes = build(plan.load())
    if args.limit:
        boxes = boxes[: args.limit]

    per_folder: dict[str, int] = {}
    for b in boxes:
        per_folder[b.folder] = per_folder.get(b.folder, 0) + 1
    print(f"primitives: {len(boxes)}")
    for f in sorted(per_folder):
        print(f"  {per_folder[f]:4d}  {f}")
    print(f"  extent    X {min(b.cx - b.sx / 2 for b in boxes):.0f}"
          f"..{max(b.cx + b.sx / 2 for b in boxes):.0f}"
          f"   Y {min(b.cy - b.sy / 2 for b in boxes):.0f}"
          f"..{max(b.cy + b.sy / 2 for b in boxes):.0f}")

    if not args.apply:
        print("\ndry run — pass --apply to spawn these into", args.level)
        for b in boxes[:6]:
            print(f"  {b.label:16s} c=({b.cx:.1f},{b.cy:.1f})")
        return 0

    from ue_mcp import Mcp, text_of

    mcp = Mcp()
    scene = "editor_toolset.toolsets.scene.SceneTools"
    app = "EditorToolset.EditorAppToolset"
    prog = "editor_toolset.toolsets.programmatic.ProgrammaticToolset"

    def js(result):
        try:
            return json.loads(text_of(result))
        except Exception:
            return {}

    def current_level() -> str:
        return js(mcp.call_tool(scene, "get_current_level")).get("returnValue") or ""

    if "true" in text_of(mcp.call_tool(app, "IsPIERunning")).lower():
        print("refusing to build: Play-In-Editor is running")
        return 1
    if args.level not in current_level():
        print(f"opening {args.level}…")
        mcp.call_tool(scene, "load_level", {"level_path": args.level})
    if args.level not in current_level():
        print("refusing to build: could not open", args.level)
        return 1

    if args.clear:
        script = "FOLDER = " + repr(FOLDER) + "\n" + CLEAR_SCRIPT
        print("clear:", js(mcp.call_tool(prog, "execute_tool_script", {"script": script}))
              .get("returnValue", "")[:200])

    script = ("ITEMS = " + repr(json.dumps([b.as_args() for b in boxes])) + "\n" + SPAWN_SCRIPT)
    result = js(mcp.call_tool(prog, "execute_tool_script", {"script": script}))
    print("spawn:", str(result.get("returnValue"))[:600])
    print("save the level in the editor (Ctrl+S) to keep it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
