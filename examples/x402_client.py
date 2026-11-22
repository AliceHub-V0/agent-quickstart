#!/usr/bin/env python3
"""Smallest AliceHub x402 client (Python standard library only).

Discovers the catalog, calls a free preview, makes one unpaid call and
decodes both forms of the payment requirement (header and body).
It never pays: no wallet, no key, no signature.

Usage: python3 x402_client.py [route]   (default: cheapest route)
"""
import base64, json, sys, time, urllib.error, urllib.request

BASE = "https://api.alicehub.app"
UA = "alicehub-agent-quickstart/0.1"


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:  # 402 lands here
        return e.code, dict(e.headers), e.read()


def header(headers, name):
    for k, v in headers.items():
        if k.lower() == name.lower():
            return v
    return None


def b64json(value):
    pad = "=" * (-len(value) % 4)
    try:
        raw = base64.b64decode(value + pad)
    except Exception:
        raw = base64.urlsafe_b64decode(value + pad)
    return json.loads(raw)


def main():
    # 1. Discover
    status, _, body = get("/x402/catalog")
    catalog = json.loads(body)
    routes = catalog["modules"]  # list of {route, url, methods, price_usdc, params, output_schema, ...}
    print(f"catalog: HTTP {status}, {len(routes)} routes, wire {catalog.get('wire')}")
    for r in routes:
        print(f"  {r['route']}: {r['price_usdc']} USDC {r['methods']}")
    if len(sys.argv) > 1:
        route = sys.argv[1]
    else:
        no_input = [r for r in routes if not r.get("params")] or routes
        route = min(no_input, key=lambda r: float(r["price_usdc"]))["route"]
    time.sleep(2)

    # 2. Free preview
    status, _, body = get(route + "?preview=1")
    print(f"\npreview {route}: HTTP {status}")
    print(json.dumps(json.loads(body), indent=2)[:800])
    time.sleep(2)

    # 3. Unpaid call -> 402
    status, headers, body = get(route)
    print(f"\nunpaid {route}: HTTP {status}")
    hv = header(headers, "payment-required")
    if hv:
        v2 = b64json(hv)
        print("header payment-required (v2), decoded:")
        for a in v2.get("accepts", []):
            # v2 uses `amount` and a CAIP-2 network id (eip155:8453 = Base)
            print(f"=> v2 {a.get('scheme')} on {a.get('network')}: {int(a['amount']) / 1_000_000} USDC to {a.get('payTo')}")
    else:
        print("no payment-required header")
    try:
        req_body = json.loads(body)
        print("body (v1 form):")
        for a in req_body.get("accepts", []):
            # v1 uses `maxAmountRequired` and the network name "base"
            amt = a.get("maxAmountRequired")
            if amt is not None:
                print(f"=> v1 {a.get('scheme')} on {a.get('network')}: {int(amt) / 1_000_000} USDC to {a.get('payTo')}")
    except ValueError:
        print("body is not JSON:", body[:200])


if __name__ == "__main__":
    main()
