# AliceHub agent quickstart

Small, dependency-free examples for developers of software agents that use the public AliceHub API.

- Base URL: `https://api.alicehub.app`
- No account and no key: the read-only MCP endpoint is free; the data routes are paid per call in USDC on Base through the [x402](https://x402.org) protocol.
- Human-readable guide: https://alicehub.app/agents/quickstart

## Requirements
Python 3.9 or later. Standard library only.

## 1. MCP
```
python3 examples/mcp_client.py seo
```
Calls `initialize`, `tools/list`, then `catalog_search` on `POST https://api.alicehub.app/mcp` (JSON-RPC 2.0, protocol `2025-06-18`, no authentication).

- `catalog_search`, `service_status`, `marketplace_listings` and `paid_menu` are free and read-only.
- Each `paid_*` tool matches one paid x402 route. Called through MCP it charges nothing: it returns an error result carrying the payment requirement (x402 v2, with the v1 body too) and the exact HTTP request to retry with a payment header. The paid answer itself comes from the HTTP route (section 2).
- Read the tool list from `tools/list`; it can change.

## 2. x402 (pay per call), without paying
```
python3 examples/x402_client.py              # cheapest route without input
python3 examples/x402_client.py /x402/intel  # a given route
```
It:
1. reads the menu at `GET /x402/catalog` (the list of routes is under `modules`);
2. calls a free sample with `?preview=1`;
3. calls the route unpaid and decodes the `402 Payment Required` answer in both forms:
   - **v2**: base64 JSON in the `payment-required` header; `accepts[].amount`, network `eip155:8453`; you answer with the `PAYMENT-SIGNATURE` header;
   - **v1**: JSON body; `accepts[].maxAmountRequired`, network `base`; you answer with the `X-PAYMENT` header.

Amounts are USDC atomic units (6 decimals). **Never hard-code a price**: read it from the menu or from the 402 answer.

These examples never sign or send a payment. To pay, use a maintained x402 client with your own wallet, and start with the cheapest route.

## Other public documents
- OpenAPI: https://api.alicehub.app/openapi.json
- Agent card: https://api.alicehub.app/.well-known/agent-card.json
- llms.txt: https://alicehub.app/llms.txt

## Security
See [SECURITY.md](SECURITY.md).

## License
MIT, see [LICENSE](LICENSE).
