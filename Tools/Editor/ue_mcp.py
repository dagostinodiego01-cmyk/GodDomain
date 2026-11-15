#!/usr/bin/env python3
"""Talk to the Unreal Editor's MCP server from the command line.

The editor serves Model Context Protocol over HTTP on 127.0.0.1:8000 (see
Docs/MCP_SETUP.md). Tool search is on, so every real tool is reached through the
`call_tool` meta-tool; this script handles the handshake, the session header and
the event-stream framing so a call is one line.

    python Tools/Editor/ue_mcp.py list
    python Tools/Editor/ue_mcp.py toolsets
    python Tools/Editor/ue_mcp.py describe actor.ActorTools
    python Tools/Editor/ue_mcp.py call actor.ActorTools find_actors '{"label": "Floor"}'

Calls run serially on the editor's game thread. Do not run two at once.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/mcp"
TIMEOUT = 300


class Mcp:
    def __init__(self, url: str = URL):
        self.url = url
        self.session = None
        self.next_id = 0
        self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "gd-tools", "version": "1.0"},
            },
        )
        self._notify("notifications/initialized")

    # -- transport ---------------------------------------------------------
    def _post(self, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session = sid
            raw = resp.read().decode("utf-8", "replace")
            ctype = resp.headers.get("Content-Type", "")
        return raw, ctype

    @staticmethod
    def _payload(raw: str, ctype: str):
        """Return the JSON-RPC message out of a plain or event-stream response."""
        if "event-stream" not in ctype:
            return json.loads(raw) if raw.strip() else None
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        return None

    def _notify(self, method: str):
        payload = {"jsonrpc": "2.0", "method": method}
        try:
            self._post(payload)
        except urllib.error.HTTPError:
            pass  # notifications may answer 202/204; the handshake still holds

    # -- requests ----------------------------------------------------------
    def _rpc(self, method: str, params: dict | None = None):
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            payload["params"] = params
        raw, ctype = self._post(payload)
        msg = self._payload(raw, ctype)
        if msg is None:
            return None
        if "error" in msg:
            raise RuntimeError(f"{method}: {msg['error']}")
        return msg.get("result")

    def list_tools(self):
        return self._rpc("tools/list", {})

    def call_meta(self, name: str, arguments: dict | None = None):
        return self._rpc("tools/call", {"name": name, "arguments": arguments or {}})

    def call_tool(self, toolset: str, tool: str, arguments: dict | None = None):
        args = {"toolset_name": toolset, "tool_name": tool}
        if arguments:
            args["arguments"] = arguments
        return self.call_meta("call_tool", args)


def text_of(result) -> str:
    """Flatten an MCP tool result to text (content blocks, or the raw value)."""
    if result is None:
        return ""
    blocks = result.get("content") if isinstance(result, dict) else None
    if blocks:
        out = []
        for b in blocks:
            out.append(b.get("text") if b.get("type") == "text" else json.dumps(b))
        return "\n".join(out)
    return json.dumps(result, indent=1)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    mcp = Mcp()
    cmd = argv[1]
    if cmd == "list":
        print(text_of(mcp.list_tools()))
    elif cmd == "toolsets":
        print(text_of(mcp.call_meta("list_toolsets")))
    elif cmd == "describe":
        print(text_of(mcp.call_meta("describe_toolset", {"toolset_name": argv[2]})))
    elif cmd == "call":
        args = json.loads(argv[4]) if len(argv) > 4 else None
        print(text_of(mcp.call_tool(argv[2], argv[3], args)))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
