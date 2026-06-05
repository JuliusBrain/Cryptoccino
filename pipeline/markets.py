"""Top 10 cryptocurrencies by market cap from CoinMarketCap.

One call per daily run. The Claude curation call never sees prices, so they
cannot be hallucinated. On any error (missing key, network, parse, rate limit),
returns an empty list and the daily issue silently omits the price strip.

Env:
- CMC_API_KEY        required; without it, fetch is skipped.
- EXCLUDE_STABLES    optional; "1"/"true"/"yes" drops dollar pegs and backfills.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

ENDPOINT = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
REQUEST_TIMEOUT_S = 15
STABLES = {"USDT", "USDC", "DAI", "TUSD", "FDUSD", "USDE", "USDS", "PYUSD"}


def _exclude_stables_flag():
    return os.getenv("EXCLUDE_STABLES", "").strip().lower() in ("1", "true", "yes")


def fetch_markets():
    """Return up to 10 coins by market cap. Empty list on any failure."""
    api_key = os.getenv("CMC_API_KEY")
    if not api_key:
        logger.warning("CMC_API_KEY not set; skipping market strip.")
        return []

    exclude_stables = _exclude_stables_flag()
    limit = 15 if exclude_stables else 10

    params = {"start": 1, "limit": limit, "convert": "USD"}
    headers = {"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"}

    try:
        response = requests.get(
            ENDPOINT, params=params, headers=headers, timeout=REQUEST_TIMEOUT_S
        )
        response.raise_for_status()
        data = response.json().get("data", [])
    except Exception as exc:
        logger.warning("Market fetch failed: %s: %s", exc.__class__.__name__, exc)
        return []

    coins = []
    for coin in data:
        symbol = (coin.get("symbol") or "").upper()
        if exclude_stables and symbol in STABLES:
            continue
        quote_usd = (coin.get("quote") or {}).get("USD") or {}
        coins.append({
            "rank": len(coins) + 1,
            "symbol": symbol,
            "name": coin.get("name") or "",
            "price": quote_usd.get("price") or 0,
            "change_24h": quote_usd.get("percent_change_24h") or 0,
        })
        if len(coins) == 10:
            break
    return coins


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    coins = fetch_markets()
    print(json.dumps(coins, indent=2))
    print(f"\n{len(coins)} coins fetched.")
