"""Re-shoot the layout evidence frames from the live V3 level.

    python Tools/Editor/shoot_views.py            # editor viewport frames
    python Tools/Editor/shoot_views.py --pie      # plus one frame from Play-In-Editor

Every frame is written to Docs/Layout as PNG. The camera poses are the ones the
layout record quotes, so a re-shoot after a rebuild is one command and the frames
stay comparable with the ones in docs.
"""

import base64
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ue_mcp import Mcp, text_of  # noqa: E402

APP = "EditorToolset.EditorAppToolset"
OUT = pathlib.Path("Docs/Layout")

NO_ANN = {"gridSpacing": 0, "gridExtent": 0, "gridHeight": 0, "maxLabelDistance": 0,
          "classFilter": None, "maxLabels": 0}
# 30 m grid on the ground plane: the top-down is read against the plan's own grid
GRID30 = dict(NO_ANN, gridSpacing=3000, gridExtent=24000, gridHeight=0)


def pose(x, y, z, pitch, yaw=90.0, roll=0.0):
    """Metres in, centimetres out — the editor's units."""
    return {"location": {"x": x * 100, "y": y * 100, "z": z * 100},
            "rotation": {"pitch": pitch, "yaw": yaw, "roll": roll},
            "scale": {"x": 1, "y": 1, "z": 1}}


VIEWS = [
    # name                         camera                         annotations
    ("Level_Arrival_V3.png",       pose(0, -160, 2.0, 8),         NO_ANN),
    ("Level_Gate_V3.png",          pose(0, -113, 3.2, 5),         NO_ANN),
    ("Level_River_V3.png",         pose(58, -127, 5.0, -8, 191),  NO_ANN),
    # yaw 270 puts east on the right and south at the top — a straight rotation of
    # the plan rather than its mirror image (a downward camera cannot do the latter)
    ("Level_Top_V3.png",           pose(0, 0, 250, -89.5, 270),   GRID30),
    ("Level_Town_V3.png",          pose(-250, -250, 210, -32, 42), NO_ANN),
]


def find_image(node):
    """Pull {mimeType, data} out of whatever shape the tool answered with."""
    if isinstance(node, dict):
        if "data" in node and isinstance(node.get("data"), str):
            return node
        for v in node.values():
            got = find_image(v)
            if got:
                return got
    elif isinstance(node, list):
        for v in node:
            got = find_image(v)
            if got:
                return got
    return None


def shoot(mcp, name, transform, ann):
    mcp.call_tool(APP, "SetCameraTransform", {"transform": transform})
    time.sleep(0.7)
    raw = text_of(mcp.call_tool(APP, "CaptureViewport",
                                {"captureTransform": transform,
                                 "annotations": ann, "bShowUI": False}))
    img = find_image(json.loads(raw))
    if not img:
        print(f"  {name}: no image in answer {raw[:160]}")
        return False
    path = OUT / name
    path.write_bytes(base64.b64decode(img["data"]))
    print(f"  {name}: {path.stat().st_size // 1024} KB")
    return True


def main():
    mcp = Mcp()
    ok = all([shoot(mcp, n, t, a) for n, t, a in VIEWS])
    if "--pie" in sys.argv:
        mcp.call_tool(APP, "StartPIE", {"options": {
            "bSimulate": False, "playMode": "PlayMode_InViewPort", "warmupSeconds": 6}})
        time.sleep(9)
        try:
            shoot(mcp, "Level_Arrival_V3_PIE.png", pose(0, -160, 1.65, 2), NO_ANN)
        finally:
            # a failed capture must never leave the editor stuck in Play mode
            try:
                mcp.call_tool(APP, "StopPIE", {})
            except Exception as exc:  # noqa: BLE001
                print("  StopPIE:", exc)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
