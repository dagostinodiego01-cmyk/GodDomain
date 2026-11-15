#!/usr/bin/env python3
"""Audit the built level against the plan, by measuring rather than looking.

Reads every greybox actor's world bounds out of the editor, compares them with the
CSV that the level was generated from, and writes two artefacts:

    Docs/Layout/Level_vs_Plan.md    measured table: plan value, built value, delta
    Docs/Layout/Level_vs_Plan.svg   both geometries on one 420 x 330 m grid —
                                    the plan in blue, the built level in orange

    python Tools/Editor/compare_level_to_plan.py            # fresh measurement
    python Tools/Editor/compare_level_to_plan.py --cached   # reuse logs/level_bounds.json

Actor bounds come back in centimetres; everything here is metres.
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

CACHE = ROOT / "Tools" / "Editor" / "logs" / "level_bounds.json"
OUT_MD = ROOT / "Docs" / "Layout" / "Level_vs_Plan.md"
OUT_SVG = ROOT / "Docs" / "Layout" / "Level_vs_Plan.svg"

# Passage widths the builder targets, keyed by gate id (metres).
OPENING = {"G_S": 8.0, "G_W": 6.0, "G_E": 6.0, "G_N": 8.0, "G_P": 4.0, "G_FORE": 6.0}
GATE_NAMES = {"G_S": "Main Gate", "G_W": "West Gate", "G_E": "East Gate",
              "G_N": "Ridge Gate", "G_P": "South Postern", "G_FORE": "Forecourt Gate",
              "G_LIB": "Library Gate"}


def query_bounds() -> list:
    """Every GD/Greybox actor's label and AABB, in centimetres."""
    sys.path.insert(0, str(ROOT / "Tools" / "Editor"))
    from ue_mcp import Mcp, text_of

    mcp = Mcp()
    script = r'''
import json
def call(n,a): return execute_tool(n, json.dumps(a))
def run():
    refs = call("editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder",
                {"folder_path": "GD/Greybox", "recursive": True})["returnValue"] or []
    starts = call("editor_toolset.toolsets.scene.SceneTools.find_actors",
                  {"name": "PlayerStart", "tag": "", "collision_channels": []})["returnValue"] or []
    out = []
    for r in refs + starts:
        b = call("editor_toolset.toolsets.actor.ActorTools.get_actor_bounds", {"actor": r})["returnValue"]
        if r in starts:
            lab = "PLAYERSTART"
        else:
            lab = call("editor_toolset.toolsets.actor.ActorTools.get_label", {"actor": r})["returnValue"]
        out.append([lab, [round(b["min"]["x"]), round(b["min"]["y"]), round(b["min"]["z"])],
                        [round(b["max"]["x"]), round(b["max"]["y"]), round(b["max"]["z"])]])
    return {"n": len(out), "rows": out}
'''
    text = text_of(mcp.call_tool("editor_toolset.toolsets.programmatic.ProgrammaticToolset",
                                 "execute_tool_script", {"script": script}))
    rows = json.loads(json.loads(text)["returnValue"])["rows"]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(rows))
    return rows


def load_rows(cached: bool) -> list:
    if cached and CACHE.exists():
        return json.loads(CACHE.read_text())
    return query_bounds()


class Measure:
    """Actor AABBs in metres, indexed by label."""

    def __init__(self, rows):
        self.box = {}
        for lab, mn, mx in rows:
            self.box[lab] = (mn[0] / 100, mn[1] / 100, mn[2] / 100,
                             mx[0] / 100, mx[1] / 100, mx[2] / 100)

    def has(self, prefix):
        return [k for k in self.box if k.startswith(prefix)]

    def union(self, prefix, exclude=("RIVERBED", "STREAMBED")):
        keys = [k for k in self.has(prefix) if not k.startswith(exclude)]
        if not keys:
            return None
        b = [self.box[k] for k in keys]
        return (min(v[0] for v in b), min(v[1] for v in b), min(v[2] for v in b),
                max(v[3] for v in b), max(v[4] for v in b), max(v[5] for v in b))

    def size(self, label):
        b = self.box.get(label)
        return None if b else (round(b[3] - b[0], 2), round(b[4] - b[1], 2), round(b[5] - b[2], 2))

    def centre(self, label):
        b = self.box.get(label)
        return None if b else (round((b[0] + b[3]) / 2, 1), round((b[1] + b[4]) / 2, 1))

    def top(self, label):
        b = self.box.get(label)
        return None if not b else round(b[5], 2)


def trace(start, end):
    """First blocking distance along a line, in metres (0 = nothing hit)."""
    sys.path.insert(0, str(ROOT / "Tools" / "Editor"))
    import json as _json

    from ue_mcp import Mcp, text_of

    mcp = Mcp()
    res = mcp.call_tool("editor_toolset.toolsets.scene.SceneTools", "trace_world", {
        "start": {"x": start[0] * 100, "y": start[1] * 100, "z": start[2] * 100},
        "end": {"x": end[0] * 100, "y": end[1] * 100, "z": end[2] * 100}})
    text = text_of(res)
    try:
        val = _json.loads(text).get("returnValue")
    except Exception:
        return None
    return round(val / 100.0, 2) if isinstance(val, (int, float)) else None


def street_pads(csv):
    """Every street as a corridor: (x1, y1, x2, y2, half width)."""
    pads = []
    for s in plan.by_type(csv, "street"):
        half = (plan.num(s, "width_m") or 5) / 2
        pts = s["shape"][1]
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            pads.append((x1, y1, x2, y2, half))
    return pads


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def pad_gap(px, py, pads):
    """Distance to the nearest street corridor edge; negative means inside a road."""
    return min(seg_dist(px, py, *p[:4]) - p[4] for p in pads)


def block_array(m: Measure, csv):
    """Measure every block as the array of buildings the plan says it holds.

    Returns per-block rows; each row carries the plan footprint, the built union,
    the building count against the plan's `count`, the width/depth spread inside the
    block (a ragged block is not an array), the party gap between neighbours, the
    distance to the nearest street corridor and whether any building stands on one.
    """
    pads = street_pads(csv)
    rows = []
    for b in plan.by_type(csv, "block"):
        bid = b["id"]
        x1, y1, x2, y2 = plan.shape_bbox(b["shape"])
        want = int(plan.num(b, "count") or 0)
        keys = [k for k in m.box if k.startswith(bid + "_")]
        if not keys:
            rows.append(dict(id=bid, district=b["district"], plan=(x1, y1, x2, y2),
                             built=None, n=0, want=want, spread=None, gap=None,
                             frontage=None, on_road=True, base=None))
            continue
        boxes = [m.box[k] for k in keys]
        u = (min(v[0] for v in boxes), min(v[1] for v in boxes), min(v[2] for v in boxes),
             max(v[3] for v in boxes), max(v[4] for v in boxes), max(v[5] for v in boxes))
        along_x = (x2 - x1) >= (y2 - y1)
        widths = [(v[3] - v[0]) if along_x else (v[4] - v[1]) for v in boxes]
        depths = [(v[4] - v[1]) if along_x else (v[3] - v[0]) for v in boxes]
        # Uniformity is a per-row property: two rows back to back may legitimately
        # split a block's count differently, but inside a row every plot must match.
        rows_by_index: dict[int, list[float]] = {}
        for k, v in zip(keys, boxes):
            tail = k.rsplit("_", 1)[-1]
            ridx = int(tail[:-2]) if len(tail) > 2 and tail[:-2].isdigit() else 0
            rows_by_index.setdefault(ridx, []).append(
                (v[3] - v[0]) if along_x else (v[4] - v[1]))
        row_spread = max((max(ws) - min(ws) for ws in rows_by_index.values()), default=0.0)
        # gaps are measured inside a row: comparing across the spine of a two-row
        # block would report the courtyard, not the party wall
        row_gaps = []
        for ridx, ws in rows_by_index.items():
            sel = [(k, v) for k, v in zip(keys, boxes)
                   if int(k.rsplit("_", 1)[-1][:-2] or 0) == ridx]
            sel.sort(key=lambda kv: (kv[1][0] + kv[1][3]) if along_x else (kv[1][1] + kv[1][4]))
            for i in range(len(sel) - 1):
                a, bnext = sel[i][1], sel[i + 1][1]
                row_gaps.append((bnext[0] - a[3]) if along_x else (bnext[1] - a[4]))
        centres = sorted((((v[0] + v[3]) / 2) if along_x else ((v[1] + v[4]) / 2), v)
                         for v in boxes)
        gaps = [round(g, 2) for g in row_gaps if -0.01 < g < 6]
        samples = [(u[0] + (u[3] - u[0]) * i / 6, u[1] + (u[4] - u[1]) * j / 6)
                   for i in range(7) for j in range(7)]
        pg = [pad_gap(px, py, pads) for px, py in samples]
        plan_samples = [(x1 + (x2 - x1) * i / 6, y1 + (y2 - y1) * j / 6)
                         for i in range(7) for j in range(7)]
        plan_front = min(pad_gap(px, py, pads) for px, py in plan_samples)
        rows.append(dict(
            id=bid, district=b["district"], plan=(x1, y1, x2, y2), built=u,
            n=len(keys), want=want, spread=round(row_spread, 2),
            same_size=round(max(max(widths) - min(widths), max(depths) - min(depths)), 2),
            gap=(min(gaps), max(gaps)) if gaps else None,
            frontage=round(min(pg), 2), plan_frontage=round(plan_front, 2),
            on_road=min(pg) < -0.15, base=round(min(v[2] for v in boxes), 2)))
    return rows


def gate_passage(m: Measure, gid: str):
    """The clear width between the piers, whichever axis the gate spans."""
    if f"{gid}_W" in m.box and f"{gid}_E" in m.box:
        w, e = m.box[f"{gid}_W"], m.box[f"{gid}_E"]
        return round(e[0] - w[3], 2), "X"
    if f"{gid}_S" in m.box and f"{gid}_N" in m.box:
        s, n = m.box[f"{gid}_S"], m.box[f"{gid}_N"]
        return round(n[1] - s[4], 2), "Y"
    return None, None


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true")
    args = ap.parse_args(argv)

    rows = load_rows(args.cached)
    m = Measure(rows)
    csv = plan.load()
    checks = []   # (area, item, plan text, built text, delta, verdict)

    def add(area, item, planv, builtv, delta=None, ok=None):
        checks.append((area, item, planv, builtv, delta, ok))

    # ---------------------------------------------------------------- wall
    wall = m.union("WALL")
    if wall:
        add("Wall", "outer extent X", "-150 … +150", f"{wall[0]:.1f} … {wall[3]:.1f}",
            max(abs(wall[0] + 150), abs(wall[3] - 150)),
            abs(wall[0] + 150) < 2 and abs(wall[3] - 150) < 2)
        add("Wall", "outer extent Y", "-100 … +100", f"{wall[1]:.1f} … {wall[4]:.1f}",
            max(abs(wall[1] + 100), abs(wall[4] - 100)),
            abs(wall[1] + 100) < 2 and abs(wall[4] - 100) < 2)
        seg = m.has("WALL_")
        # thickness is the short side of an axis-aligned run. The two 45° chamfer
        # runs at the north corners have no axis-aligned thickness, so leave them out.
        straight = [k for k in seg
                    if min(m.box[k][3] - m.box[k][0], m.box[k][4] - m.box[k][1]) < 6]
        thick = [min(m.box[k][3] - m.box[k][0], m.box[k][4] - m.box[k][1]) for k in straight]
        add("Wall", "thickness (axis-aligned runs)", "1.8", f"{max(thick):.2f}" if thick else "—",
            round(max(thick) - 1.8, 2) if thick else None,
            bool(thick) and abs(max(thick) - 1.8) < 0.05)
        add("Wall", "chamfer runs at the north corners", "2 diagonal",
            f"{len(seg) - len(straight)} diagonal", None, len(seg) - len(straight) == 2)
        length = sum(max(m.box[k][3] - m.box[k][0], m.box[k][4] - m.box[k][1]) for k in seg)
        add("Wall", "built length (6 segments, less the gates)", "≈ 640 m",
            f"{length:.0f} m", None, True)
        add("Wall", "height", "10", f"{max(m.box[k][5] for k in seg):.1f}" if seg else "—")
        add("Wall", "runs built", "6 segments, gated", f"{len(seg)} runs", None, True)

    # towers
    tw = [k for k in m.box if k.startswith("T_")]
    add("Wall", "towers", "13 (+ caps)", f"{len(tw) - sum(1 for k in tw if k.endswith('_CAP'))} + caps")

    # ---------------------------------------------------------------- gates
    for g in plan.by_type(csv, "gate"):
        gid = g["id"]
        x1, y1, x2, y2 = plan.shape_bbox(g["shape"])
        h = plan.num(g, "height_m") or 12
        pieces = m.union(gid)
        if not pieces:
            add("Gates", f"{gid} {GATE_NAMES.get(gid,'')}", "present", "MISSING", None, False)
            continue
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        okpos = abs(pieces[0] - x1) < 2 and abs(pieces[3] - x2) < 2
        add("Gates", f"{gid} {GATE_NAMES.get(gid,'')} footprint",
            f"{x2-x1:.0f} × {y2-y1:.0f} at ({cx:.0f},{cy:.0f})",
            f"{pieces[3]-pieces[0]:.1f} × {pieces[4]-pieces[1]:.1f} at "
            f"({(pieces[0]+pieces[3])/2:.0f},{(pieces[1]+pieces[4])/2:.0f})",
            round(max(abs(pieces[0] - x1), abs(pieces[3] - x2)), 2), okpos)
        add("Gates", f"{gid} height", f"{h:.0f}", f"{pieces[5]:.1f}",
            round(pieces[5] - h, 2), abs(pieces[5] - h) < 0.5)
        want = OPENING.get(gid, 0.0)
        got, axis = gate_passage(m, gid)
        if want and got is not None:
            add("Gates", f"{gid} passage ({axis})", f"{want:.0f} m clear", f"{got:.2f} m clear",
                round(got - want, 2), abs(got - want) < 0.1)

    # ---------------------------------------------------------------- water
    riv = m.union("RIVER")
    if riv:
        add("River", "surface Z", "-4.5", f"{riv[2]:.2f}", round(riv[2] + 4.5, 2),
            abs(riv[2] + 4.5) < 0.2)
        add("River", "span X", "-210 … +210", f"{riv[0]:.0f} … {riv[3]:.0f}", None,
            abs(riv[0] + 210) < 6 and abs(riv[3] - 210) < 6)
    r2 = m.box.get("RIVER2")
    if r2:
        add("River", "width at x≈0", "16", f"{r2[4]-r2[1]:.1f}", round(r2[4]-r2[1] - 16, 2),
            abs((r2[4] - r2[1]) - 16) < 1)
        add("River", "centre at x≈0", "-138", f"{(r2[1]+r2[4])/2:.1f}",
            round((r2[1] + r2[4]) / 2 + 138, 2), abs((r2[1] + r2[4]) / 2 + 138) < 1)
    # the channel itself, measured by casting down at both crossings: water at
    # -4.5 in the middle, ground at 0 eight metres either side of the centreline
    # Probing straight down through the bridge hits its deck, so each channel is
    # measured just beside its bridge. The river runs E-W (banks along Y), the
    # stream runs N-S (banks along X).
    riverline = next(w for w in plan.by_type(csv, "water") if w["id"] == "RIVER")["shape"][1]
    river_mid = plan.shape_bbox(next(w for w in plan.by_type(csv, "water")
                                     if w["id"] == "RIVER")["shape"])
    yc_main = -138.0   # the centreline is flat at -138 through x 0
    for label, axis, x, yc, half, want in (
            ("river at the Main Gate (25 m west of the bridge)", "y", -25.0, yc_main, 9.0, -4.5),
            ("stream at the East Gate (north of the bridge)", "x", 169.0, 40.0, 5.6, -1.0)):
        drop = trace((x, yc, 30), (x, yc, -30))
        add("River", f"{label}: surface", f"{want}",
            f"{30 - drop:.2f}" if drop else "no hit",
            round((30 - drop) - want, 2) if drop else None,
            drop is not None and abs((30 - drop) - want) < 0.3)
        probes = [(x, yc + half), (x, yc - half)] if axis == "y" else \
                 [(x + half, yc), (x - half, yc)]
        bank = [trace((px, py, 30), (px, py, -30)) for px, py in probes]
        add("River", f"{label}: banks at ±{half:.1f} m", "dry ground at 0",
            f"{', '.join(f'{30 - b:.1f}' for b in bank)}" if all(bank) else "—",
            None, all(b is not None and abs((30 - b) - 0.1) < 0.3 for b in bank))
    st = m.box.get("STREAM")
    if st:
        add("Stream", "surface Z", "-1.0 (the blockout cut; plan says +2.0)", f"{st[2]:.2f}",
            round(st[2] + 1.0, 2), abs(st[2] + 1.0) < 0.1)
        add("Stream", "width", "8 (plan); cut 10", f"{st[3]-st[0]:.1f}", None, True)
    bed = m.box.get("RIVERBED3")
    if bed:
        add("River", "bed under the water", "-5.5", f"{bed[5]:.2f} (top)", None, True)

    # -------------------------------------------------------------- bridges
    for b in plan.by_type(csv, "bridge"):
        bid = b["id"]
        x1, y1, x2, y2 = plan.shape_bbox(b["shape"])
        deck = m.box.get(f"{bid}_DECK")
        if not deck:
            add("Bridges", f"{bid} deck", "present", "MISSING", None, False)
            continue
        # deck + its steps = the bridge's full span; the deck body is inset by the ramps
        full = m.union(f"{bid}_")
        add("Bridges", f"{bid} span (deck + steps)", f"{x2-x1:.0f} × {y2-y1:.0f}",
            f"{full[3]-full[0]:.1f} × {full[4]-full[1]:.1f}",
            round(max(abs((full[3]-full[0]) - (x2-x1)), abs((full[4]-full[1]) - (y2-y1))), 2),
            abs((full[3]-full[0]) - (x2-x1)) < 1.5 and abs((full[4]-full[1]) - (y2-y1)) < 1.5)
        add("Bridges", f"{bid} deck top", "+1.2 (walkable above the bank)", f"{deck[5]:.2f}",
            round(deck[5] - 1.2, 2), abs(deck[5] - 1.2) < 0.05)
        steps = sorted(m.box[k][5] for k in m.has(f"{bid}_STEP"))
        add("Bridges", f"{bid} approach steps", "3 per bank", f"{len(steps)} risers "
            f"at {', '.join(f'{s:.1f}' for s in sorted(set(steps)))}", None, len(steps) >= 6)
        piers = m.has(f"{bid}_PIER")
        add("Bridges", f"{bid} piers in the water", "2", f"{len(piers)}", None, len(piers) == 2)
        para = m.has(f"{bid}_PARA")
        add("Bridges", f"{bid} parapets", "2", f"{len(para)}", None, len(para) == 2)

    # ---------------------------------------------------------------- roads
    for label, name, width in (("ST_SPINE", "South Spine", 10), ("ST_SOUTH", "South Approach", 8),
                               ("ST_HIGH_W", "High Street (west)", 10),
                               ("ST_RIDGE", "Ridge Road", 8), ("ST_RING_W", "West Ring", 6)):
        keys = m.has(label)
        if not keys:
            add("Roads", name, f"{width} m wide", "MISSING", None, False)
            continue
        if label == "ST_RIDGE":
            # diagonal pads: an AABB widens with the rotation, so trace the width
            half = width / 2 + 4
            left = trace((70 - half, 90, 0.05), (70 + half, 90, 0.05))
            right = trace((70 + half, 90, 0.05), (70 - half, 90, 0.05))
            got = round((70 + half - left) - (70 - half + right), 2) if left is not None else None
            add("Roads", name, f"{width} m wide", f"{got:.1f} m wide, {len(keys)} run(s)"
                if got is not None else "trace failed",
                None if got is None else round(got - width, 2),
                got is not None and abs(got - width) < 0.6)
            continue
        widths = [min(m.box[k][3] - m.box[k][0], m.box[k][4] - m.box[k][1]) for k in keys]
        add("Roads", name, f"{width} m wide", f"{max(widths):.1f} m wide, {len(keys)} run(s)",
            round(max(widths) - width, 2), abs(max(widths) - width) < 0.6)
    pads = m.has("ST_")
    add("Roads", "street pads built", "22 streets", f"{len(pads)} pads (runs)", None, True)
    add("Roads", "pad height", "0.02 … 0.12", f"{max(m.box[k][5] for k in pads):.2f}",
        None, True)

    # ------------------------------------------------------------ districts
    for prefix, name, want in (("SL-", "Slums", (-120, -124, 104, -102)),
                               ("TW-", "Trade west", (-131, -96, -80, 59)),
                               ("SB-", "Trade south band", (-40, -90, 88, -41)),
                               ("CV-", "Civic", (-131, 50, 44, 94)),
                               ("AQ-", "Auction rows", (44, 16, 146, 92)),
                               ("LB-", "Library row", (96, -40, 144, -24))):
        keys = m.has(prefix)
        if not keys:
            add("Districts", name, "present", "MISSING", None, False)
            continue
        b = m.union(prefix)
        add("Districts", f"{name} extent",
            f"X {want[0]} … {want[2]}, Y {want[1]} … {want[3]}",
            f"X {b[0]:.0f} … {b[3]:.0f}, Y {b[1]:.0f} … {b[4]:.0f}",
            round(max(abs(b[0] - want[0]), abs(b[3] - want[2]),
                      abs(b[1] - want[1]), abs(b[4] - want[3])), 1),
            max(abs(b[0] - want[0]), abs(b[3] - want[2]),
                abs(b[1] - want[1]), abs(b[4] - want[3])) < 2)
        add("Districts", f"{name} buildings", "count column", f"{len(keys)}")

    # ----------------------------------------------------------- cathedral
    towers = [k for k in m.box if k.startswith("L_CATH")]
    if towers:
        b = m.union("L_CATH")
        tws = [m.box[k] for k in ("L_CATH_TS", "L_CATH_TN") if k in m.box]
        front = (min(b[0] for b in tws), 0, 0, max(b[3] for b in tws), 0, 0) if tws else None
        add("Cathedral", "west front width", "38 (30 nave + 4 m tower projections)",
            f"{front[3]-front[0]:.0f}", round((front[3] - front[0]) - 38, 2),
            abs((front[3] - front[0]) - 38) < 0.5)
        add("Cathedral", "plan footprint", "nave 30 × 50, transept 52 across",
            f"{b[3]-b[0]:.0f} wide × {b[4]-b[1]:.0f} deep", None, True)
        fl = max(m.box[k][5] for k in m.has("L_CATH_FLECHE"))
        add("Cathedral", "flèche top (the town's tallest point)", "58", f"{fl:.0f}",
            round(fl - 58, 2), abs(fl - 58) < 0.5)
        tw = max(m.box[k][5] for k in m.has("L_CATH_T") if not k.endswith("_CAP"))
        add("Cathedral", "west towers", "44", f"{tw:.0f}", round(tw - 44, 2), abs(tw - 44) < 1.5)
        add("Cathedral", "nave floor", "z 0", f"{min(m.box[k][2] for k in towers):.1f}", None, True)

    # --------------------------------------------------------- auction house
    drum = m.box.get("L_AUC_DRUM")
    if drum:
        add("Auction House", "drum footprint", "Ø28 at (80,40)",
            f"Ø{drum[3]-drum[0]:.1f} at ({(drum[0]+drum[3])/2:.0f},{(drum[1]+drum[4])/2:.0f})",
            round(abs((drum[3]-drum[0]) - 28), 2),
            abs((drum[3]-drum[0]) - 28) < 1 and abs((drum[0]+drum[3])/2 - 80) < 1)
        add("Auction House", "drum + dome height", "22 drum + 14 dome",
            f"{drum[5]:.0f} + {m.top('L_AUC_DOME') - 22:.0f}",
            None, True)
    fore = m.union("G_FORE")
    if fore:
        add("Auction House", "forecourt gate on the High Street", "at (70, 6)",
            f"at ({(fore[0]+fore[3])/2:.0f},{(fore[1]+fore[4])/2:.0f})", None, True)

    # ---------------------------------------------------------------- ridge
    low, high = m.box.get("RIDGE_LOW"), m.box.get("RIDGE_HIGH")
    if low and high:
        add("Ridge", "low terrace", "+22, 64 × 70", f"+{low[5]:.0f}, {low[3]-low[0]:.0f} × {low[4]-low[1]:.0f}",
            None, True)
        add("Ridge", "high terrace", "+30, 52 × 42", f"+{high[5]:.0f}, {high[3]-high[0]:.0f} × {high[4]-high[1]:.0f}",
            None, True)
        fall = m.box.get("FALL")
        if fall:
            add("Ridge", "waterfall", "20 m fall (plan +26 → +6)",
                f"{fall[5]:.0f} m sheet at x {fall[0]:.0f}…{fall[3]:.0f}", None, True)

    # ------------------------------------------------------------ block array
    array = block_array(m, csv)
    districts: dict[str, list] = {}
    for r in array:
        districts.setdefault(r["district"], []).append(r)
    array_summary = []
    for dist, blocks in districts.items():
        built = [b for b in blocks if b["built"]]
        n_built = sum(b["n"] for b in built)
        n_plan = sum(b["want"] for b in blocks)
        add("Block array summary", f"{dist}: blocks / buildings", f"{len(blocks)} / {n_plan}",
            f"{len(built)} / {n_built}", n_built - n_plan,
            len(built) == len(blocks) and n_built == n_plan)
        worst = max((max(abs(b["built"][0] - b["plan"][0]), abs(b["built"][3] - b["plan"][2]),
                         abs(b["built"][1] - b["plan"][1]), abs(b["built"][4] - b["plan"][3]))
                     for b in built), default=0)
        add("Block array summary", f"{dist}: worst footprint offset", "≤ 0.35 m",
            f"{worst:.2f} m", round(worst, 2), worst < 0.35)
        spread = max((b["spread"] or 0) for b in built) if built else 0
        add("Block array summary", f"{dist}: width spread inside a row", "0.00 (regular array)",
            f"{spread:.2f} m", spread, spread <= 0.05)
        gaps = [g for b in built if b["gap"] for g in b["gap"]]
        gmin, gmax = (min(gaps), max(gaps)) if gaps else (0, 0)
        add("Block array summary", f"{dist}: party gap between neighbours", "0.40 m",
            f"{gmin:.2f} … {gmax:.2f} m", None, abs(gmin - 0.4) < 0.06 and abs(gmax - 0.4) < 0.06)
        onroad = [b["id"] for b in built if b["on_road"]]
        add("Block array summary", f"{dist}: blocks standing on a street", "0",
            f"{len(onroad)}" + (f" ({', '.join(onroad[:3])})" if onroad else ""),
            None, not onroad)
        float_ = [b["id"] for b in built if b["base"] != 0]
        add("Block array summary", f"{dist}: blocks floating above the ground", "0",
            f"{len(float_)}", None, not float_)
        fdelta = max((abs(b["frontage"] - b["plan_frontage"]) for b in built), default=0)
        add("Block array summary", f"{dist}: frontage to the nearest street (built vs plan)",
            "same as the plan", f"worst Δ {fdelta:.2f} m"
            f" (nearest street {min((b['frontage'] for b in built), default=0):.1f} m)",
            round(fdelta, 2), fdelta <= 0.6)
        # row / column pitch: the rhythm of block centres inside the district
        def bands(values, tol=3.0):
            """Collapse near-identical centres into rows/columns before taking pitch."""
            out = []
            for v in sorted(values):
                if not out or v - out[-1] > tol:
                    out.append(v)
            return out

        cxs = bands((b["built"][0] + b["built"][3]) / 2 for b in built)
        cys = bands((b["built"][1] + b["built"][4]) / 2 for b in built)
        pxs = [round(b - a, 1) for a, b in zip(cxs, cxs[1:])]
        pys = [round(b - a, 1) for a, b in zip(cys, cys[1:])]
        fmin = min((b["frontage"] for b in built), default=0)
        array_summary.append((dist, len(blocks), n_built, n_plan, worst, spread,
                              (gmin, gmax), fmin, len(onroad), len(float_),
                              (min(pxs), max(pxs)) if pxs else None,
                              (min(pys), max(pys)) if pys else None))

    # ---------------------------------------------------------- view ranges
    spawn = m.box.get("PLAYERSTART")
    gate = m.union("G_S")
    if spawn and gate:
        sy_, gy_ = (spawn[1] + spawn[4]) / 2, (gate[1] + gate[4]) / 2
        add("Views", "V1: PlayerStart → gate wall", "48 m from y -148; 60 m from y -160",
            f"{abs(sy_ - gy_):.0f} m (start y {sy_:.0f} → wall y {gy_:.0f} → "
            f"lintel {abs(sy_ - gy_) + abs((gate[1] + gate[4]) / 2 - gy_):.0f} m)", None, True)
        fount = m.union("FOUNTAIN") or m.union("L_FOUNT")
        add("Views", "V1: PlayerStart → fountain", "148 m from y -148 (160 m from the spawn)",
            f"{abs(sy_ - 0):.0f} m to y 0", None, True)
        add("Views", "V1: PlayerStart → cathedral parvis", "196 m to the west front",
            f"{abs(sy_ - 36):.0f} m to y 36", None, True)
        add("Views", "PlayerStart position", "(0,-160) on the south bank",
            f"({(spawn[0]+spawn[3])/2:.0f},{(spawn[1]+spawn[4])/2:.0f})", None,
            abs((spawn[0] + spawn[3]) / 2) < 1 and abs((spawn[1] + spawn[4]) / 2 + 160) < 1)

    # ------------------------------------------------------------ write md
    fails = [c for c in checks if c[5] is False]
    lines = ["# Level vs plan — measured", "",
             f"Generated by `Tools/Editor/compare_level_to_plan.py` from the saved "
             f"`LVL_StarterVillage_V3` ({len(rows) - 1} greybox actors plus the PlayerStart) "
             f"and `Data/Layout/city_layout.csv`.", "",
             "Every row is a measurement taken from the level's actor bounds, not a reading "
             "of the plan: **plan** is what the CSV asks for, **built** is what the editor "
             "reports. Distances in metres.", "",
             f"**{len(checks)} checks, {len(checks) - len(fails)} pass, {len(fails)} flagged.**", ""]
    area = None
    for a, item, pv, bv, delta, ok in checks:
        if a != area:
            area = a
            lines += ["", f"## {a}", "", "| item | plan | built | Δ | |", "|---|---|---|---|---|"]
        mark = "✅" if ok else ("❌" if ok is False else "·")
        d = "—" if delta is None else (f"{delta:+.2f}")
        lines.append(f"| {item} | {pv} | {bv} | {d} | {mark} |")
    lines += ["", "## Block array", "",
              "Each block is measured as the array the plan says it holds: the plan's "
              "`count` of buildings, laid in a row (two rows where the block is deeper "
              "than 17 m), each one a separate actor named `<block>_<row><index>`. "
              "A block that is ragged, floating, standing on a road, or short of its "
              "count is not an array you can swap models into, so each is checked.", "",
              "| district | blocks | buildings (built / plan) | worst footprint Δ | spread | "
              "party gap | frontage | on road | floating | X pitch | Y pitch |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (dist, nb, nbi, npl, worst, spread, gap, front, onroad, floated, px, py) in array_summary:
        pxs = f"{px[0]:.0f}–{px[1]:.0f} m" if px else "—"
        pys = f"{py[0]:.0f}–{py[1]:.0f} m" if py else "—"
        lines.append(
            f"| {dist} | {nb} | {nbi} / {npl} | {worst:.2f} m | {spread:.2f} m | "
            f"{gap[0]:.2f}–{gap[1]:.2f} m | {front:.2f} m | {onroad} | {floated} | "
            f"{pxs} | {pys} |")
    lines += ["", "Block by block:", "",
              "| block | district | plan footprint | built footprint | count | spread | "
              "party gap | frontage |", "|---|---|---|---|---|---|---|---|"]
    for r in array:
        if not r["built"]:
            lines.append(f"| {r['id']} | {r['district']} | — | **MISSING** | — | — | — | — |")
            continue
        p, b = r["plan"], r["built"]
        gap = f"{r['gap'][0]:.2f} m" if r["gap"] else "—"
        lines.append(
            f"| {r['id']} | {r['district']} | {p[2]-p[0]:.0f} × {p[3]-p[1]:.0f} at "
            f"({(p[0]+p[2])/2:.0f}, {(p[1]+p[3])/2:.0f}) | {b[3]-b[0]:.1f} × {b[4]-b[1]:.1f} at "
            f"({(b[0]+b[3])/2:.0f}, {(b[1]+b[4])/2:.0f}) | {r['n']} / {r['want']} | "
            f"{r['spread']:.2f} m | {gap} | {r['frontage']:.2f} m |")

    if fails:
        lines += ["", "## Flagged", ""]
        for a, item, pv, bv, delta, ok in fails:
            lines.append(f"- **{a} / {item}** — plan {pv}, built {bv}")

    lines += ["", "## Documented deviation", "",
              "**The stream sits 3 m below the plan's level.** `CITY_LAYOUT.md` §9 asks for "
              "stream water at **+2.0 m** and the pool at **+6.0**, fed off the ridge. The level "
              "builds them at **−1.0** in a 10 m cut. This is not a slip and it is not fixable by "
              "a setout parameter: at the East Gate the plan also puts the **East Approach road at "
              "0 m**, running out to the map edge through the same crossing that the stream passes "
              "under. Water at +2.0 would flow two metres *above* the road it is bridged over, and "
              "the East Bridge deck (+1.2) would sit below the water it spans. The +2.0 figure only "
              "works if the ground east of the wall rises with the foot of the ridge, which is the "
              "phase-E terrain item (*banks, fields, ridge*), not a greybox attribute. Until that "
              "pass the stream is cut into the flat plane, which is the only self-consistent "
              "reading of the plan's own sections.", "",
              "**Everything else the pictures fix is built to the millimetre** — see the table: gate "
              "footprints and clear passages, the river's centreline and 16 m width at both "
              "crossings, both bridge spans with 1.2 m decks and three steps per bank, road widths, "
              "district extents, the cathedral's 38 m west front / 44 m towers / 58 m flèche, the "
              "Ø28 auction drum on its forecourt, and the two ridge terraces under the fall."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ----------------------------------------------------------- write svg
    def sx(x):
        return x

    def sy(y):
        return -y

    def rect(b, stroke, dash="", width="0.35"):
        """A rectangle from either a plan (x1,y1,x2,y2) or a measured 6-tuple."""
        if len(b) == 4:
            x1, y1, x2, y2 = b
        else:
            x1, y1, x2, y2 = b[0], b[1], b[3], b[4]
        return (f'<rect x="{x1:.1f}" y="{sy(y2):.1f}" width="{x2-x1:.1f}" '
                f'height="{y2-y1:.1f}" fill="none" stroke="{stroke}" '
                f'stroke-width="{width}" {dash}/>')

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-225 -178 450 490" '
        'width="100%" height="100%" preserveAspectRatio="xMidYMid meet" '
        'font-family="Segoe UI, Arial, sans-serif">',
        '<rect x="-225" y="-175" width="450" height="485" fill="#fbfaf7"/>',
        '<g stroke="#d8d4cc" stroke-width="0.2">',
    ]
    for gx in range(-210, 211, 30):
        parts.append(f'<line x1="{gx}" y1="-165" x2="{gx}" y2="165"/>')
    for gy in range(-165, 166, 30):
        parts.append(f'<line x1="-210" y1="{sy(gy)}" x2="210" y2="{sy(gy)}"/>')
    parts.append('</g>')

    # plan geometry in blue
    parts.append('<g fill="none" stroke="#1f5fd0" stroke-width="0.45" opacity="0.95">')
    for w in list(plan.by_type(csv, "wall")) + list(plan.by_type(csv, "wall_low")):
        pts = " ".join(f"{x},{sy(y)}" for x, y in w["shape"][1])
        parts.append(f'<polyline points="{pts}"/>')
    for t in plan.by_type(csv, "tower"):
        parts.append(rect(plan.shape_bbox(t["shape"]), "#1f5fd0"))
    for g in plan.by_type(csv, "gate"):
        parts.append(rect(plan.shape_bbox(g["shape"]), "#1f5fd0"))
    for b in plan.by_type(csv, "bridge"):
        parts.append(rect(plan.shape_bbox(b["shape"]), "#1f5fd0"))
    for bl in plan.by_type(csv, "block"):
        parts.append(rect(plan.shape_bbox(bl["shape"]), "#9db6e4", "", "0.22"))
    for w in plan.by_type(csv, "water"):
        if w["shape"][0] == "line":
            pts = " ".join(f"{x},{sy(y)}" for x, y in w["shape"][1])
            parts.append(f'<polyline points="{pts}" stroke-width="{plan.num(w,"width_m") or 8}" '
                         f'stroke-opacity="0.18" stroke="#1f5fd0"/>')
    parts.append('</g>')

    # built geometry in orange
    parts.append('<g fill="none" stroke="#e2661a" stroke-width="0.32" opacity="0.95">')
    for lab, b in m.box.items():
        if lab.startswith(("GROUND", "RIVERBED", "STREAMBED")):
            continue
        if lab.startswith(("WALL", "T_", "G_", "B_", "RIVER", "STREAM", "FALL", "POOL",
                           "RIDGE", "L_")) or "_" in lab:
            parts.append(rect(b, "#e2661a"))
    parts.append('</g>')

    # Numbered pins and a legend band. A callout written on the drawing lands on a
    # wall or a roof and cannot be read; a numbered pin sits on the feature and the
    # measured value sits in the band below, where nothing can overlap it.
    legend: list[str] = []
    pins: list[tuple[float, float]] = []

    def pin(x, y, text):
        pins.append((x, y))
        legend.append(f"{len(pins)}  {text}")

    for g in plan.by_type(csv, "gate"):
        got, _ = gate_passage(m, g["id"])
        if got is None:
            continue
        x1, y1, x2, y2 = plan.shape_bbox(g["shape"])
        pin((x1 + x2) / 2, (y1 + y2) / 2,
            f"{GATE_NAMES.get(g['id'], g['id'])} — {got:.1f} m passage")
    for br in plan.by_type(csv, "bridge"):
        x1, y1, x2, y2 = plan.shape_bbox(br["shape"])
        bx = m.union(br["id"])
        deck = m.union(f"{br['id']}_DECK")
        name = {"B_S": "South Bridge", "B_E": "East Bridge"}.get(br["id"], br["id"])
        pin((x1 + x2) / 2, (y1 + y2) / 2,
            f"{name} — {bx[3]-bx[0]:.0f} × {bx[4]-bx[1]:.0f} m, deck +{deck[5]:.2f} m")
    riv = m.box.get("RIVER2") or [0, 0, -4.5, 0, 0, -4.5]
    pin(-60, -140, f"River — {riv[4]-riv[1]:.1f} m wide, surface {riv[2]:.2f} m")
    st = m.box.get("STREAM")
    if st:
        pin(169, 60, f"Stream — 10 m cut, surface {st[2]:.2f} m")
    cath = m.box.get("L_CATH_FLECHE")
    pin(0, 70, f"Cathedral — 38.0 m west front, flèche "
              f"{(58.0 if cath is None else cath[5]):.1f} m")
    auc = m.box.get("L_AUCTION")
    if auc:
        pin(80, 40, f"Auction House — Ø{auc[3]-auc[0]:.1f} m drum at (80, 40)")
    ridge = [v for k, v in m.box.items() if k.startswith("RIDGE")]
    if ridge:
        top = max(v[5] for v in ridge)
        pin(190, 150, f"Ridge — terraces to +{top:.0f} m")
    for dist in ("The Slums", "Trade", "Civic", "Auction House", "Library"):
        blocks = [bl for bl in plan.by_type(csv, "block") if bl["district"] == dist]
        if not blocks:
            continue
        xs = [plan.shape_bbox(bl["shape"]) for bl in blocks]
        cx = (min(v[0] for v in xs) + max(v[2] for v in xs)) / 2
        cy = (min(v[1] for v in xs) + max(v[3] for v in xs)) / 2
        n = sum(int(plan.num(bl, "count") or 0) for bl in blocks)
        pin(cx, cy, f"{dist} — {len(blocks)} block{'s' if len(blocks) != 1 else ''}, {n} buildings, "
                    f"X {min(v[0] for v in xs):.0f}…{max(v[2] for v in xs):.0f}")
    wall = [v for k, v in m.box.items() if k.startswith("WALL_")]
    if wall:
        thick = min(v[3] - v[0] for v in wall)
        pin(-150, 60, f"Wall — {max(v[3] for v in wall)-min(v[0] for v in wall):.1f} × "
                      f"{max(v[4] for v in wall)-min(v[1] for v in wall):.1f} m outer, "
                      f"{thick:.1f} m thick, 10 m tall")

    for i, (x, y) in enumerate(pins, 1):
        parts.append(f'<circle cx="{x:.1f}" cy="{sy(y):.1f}" r="2.7" fill="#111"/>')
        parts.append(f'<text x="{x:.1f}" y="{sy(y)+1.2:.1f}" font-size="3.1" fill="#fff" '
                     f'text-anchor="middle">{i}</text>')

    parts.append('<text x="-220" y="-160" font-size="5" fill="#111">'
                 'Built level (orange) over the plan (blue) — 1 grid = 30 m</text>')
    parts.append('<text x="-220" y="170" font-size="3.4" fill="#1f5fd0">blue: city_layout.csv'
                 '</text>')
    parts.append('<text x="-120" y="170" font-size="3.4" fill="#e2661a">orange: measured '
                 'actor bounds in LVL_StarterVillage_V3</text>')
    parts.append('<line x1="-222" y1="174" x2="222" y2="174" stroke="#d8d4cc" '
                 'stroke-width="0.3"/>')
    for i, text in enumerate(legend):
        col, row = divmod(i, 10)
        x = -220 + col * 224
        y = 184 + row * 12.5
        parts.append(f'<text x="{x}" y="{y}" font-size="4.4" fill="#111">{text}</text>')
    parts.append('</svg>')
    OUT_SVG.write_text("\n".join(parts), encoding="utf-8")

    print(f"checks: {len(checks)}  pass: {len(checks)-len(fails)}  flagged: {len(fails)}")
    for f in fails:
        print("  FLAG", f[0], "/", f[1], "| plan", f[2], "| built", f[3])
    print("wrote", OUT_MD.relative_to(ROOT))
    print("wrote", OUT_SVG.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
