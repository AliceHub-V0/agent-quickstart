#!/usr/bin/env python3
"""Talk to the free, read-only AliceHub MCP endpoint (Python standard library only).

JSON-RPC 2.0 over HTTP, protocol version 2025-06-18, no authentication.
Usage: python3 mcp_client.py [search words]   (default: seo)
"""
import json, sys, urllib.request

URL = "https://api.alicehub.app/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "alicehub-agent-quickstart/0.1",
}


def rpc(method, params, id_):
    body = json.dumps({"jsonrpc": "2.0", "id": id_, "method": method, "params": params}).encode()
    req = urllib.request.Request(URL, data=body, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read().decode()
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    # text/event-stream: take the last "data:" line
    data = [l[5:].strip() for l in raw.splitlines() if l.startswith("data:")]
    return json.loads(data[-1])


def main():
    init = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "quickstart", "version": "0.1"}}, 1)
    print("server:", init["result"].get("serverInfo"), "protocol:", init["result"].get("protocolVersion"))
    tools = rpc("tools/list", {}, 2)["result"]["tools"]
    print("tools:", [t["name"] for t in tools])
    query = " ".join(sys.argv[1:]) or "seo"
    res = rpc("tools/call", {"name": "catalog_search", "arguments": {"query": query, "limit": 3}}, 3)
    print(json.dumps(json.loads(res["result"]["content"][0]["text"]), indent=2)[:1500])


if __name__ == "__main__":
    main()
