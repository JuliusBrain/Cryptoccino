"""Price strip data from CoinGecko's free /coins/markets endpoint.

Fetches 6 fixed coins (BTC, ETH, BNB, SOL, XRP, DOGE) with current price,
24-hour change, and the CoinGecko 7-day hourly sparkline (~168 points). Only
the most recent ~24h (the last 1/7) is kept — so the chart matches the 24h
change pill and a recent up/down move is actually visible — then downsampled
to ≤30 points so the inline SVG is light.

Fail-open contract: on any error or rate limit, falls back to the last good
response cached at assets/data/prices.json. With no usable cache, returns
None so run.py publishes the issue with no strip rather than aborting.

render_strip_html(prices, mode) produces the HTML island. mode='web' emits
inline SVG sparklines; mode='email' emits <img> tags pointing at PNGs
written via matplotlib to assets/sparklines/<TICKER>.png — for an eventual
email pipeline, since inline SVG is unreliable across mail clients.
"""

import logging
import os
from pathlib import Path

import requests

from pipeline.cache import read_json, write_json

logger = logging.getLogger(__name__)

ENDPOINT = "https://api.coingecko.com/api/v3/coins/markets"
REQUEST_TIMEOUT_S = 20
CACHE_PATH = Path("assets/data/prices.json")
SPARKLINES_DIR = Path("assets/sparklines")
SPARK_TARGET_POINTS = 30

# Fixed list of coins, in display order.
ID_TO_TICKER = [
    ("bitcoin", "BTC"),
    ("ethereum", "ETH"),
    ("binancecoin", "BNB"),
    ("solana", "SOL"),
    ("ripple", "XRP"),
    ("dogecoin", "DOGE"),
]

# Cappuccino palette (mirrors style.css :root).
UP = "#4C7A47"
DOWN = "#B14A33"
CREMA = "#A35E1E"


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def fetch_prices():
    """Return list of {ticker, price, change_24h, spark[]} or None.

    On any HTTP / parse / rate-limit failure, falls back to the JSON cache.
    With no usable cache either, returns None and the caller is expected to
    render with no strip.
    """
    params = {
        "vs_currency": "usd",
        "ids": ",".join(k for k, _ in ID_TO_TICKER),
        "sparkline": "true",
        "price_change_percentage": "24h",
    }
    headers = {"Accept": "application/json"}
    key = os.getenv("COINGECKO_KEY")
    if key:
        headers["x-cg-demo-api-key"] = key

    try:
        response = requests.get(
            ENDPOINT, params=params, headers=headers, timeout=REQUEST_TIMEOUT_S
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.warning(
            "Price fetch failed: %s: %s. Falling back to cache.",
            exc.__class__.__name__, exc,
        )
        return read_json(CACHE_PATH)

    by_id = {coin.get("id"): coin for coin in data}
    result = []
    for coin_id, ticker in ID_TO_TICKER:
        coin = by_id.get(coin_id)
        if not coin:
            continue
        raw_spark = ((coin.get("sparkline_in_7d") or {}).get("price")) or []
        result.append({
            "ticker": ticker,
            "price": coin.get("current_price") or 0,
            "change_24h": coin.get("price_change_percentage_24h") or 0,
            "spark": _downsample(_last_window(raw_spark), SPARK_TARGET_POINTS),
        })

    if not result:
        return read_json(CACHE_PATH)

    write_json(CACHE_PATH, result)
    return result


def _last_window(points, fraction=7):
    """Keep only the most recent 1/`fraction` of a sparkline series. CoinGecko's
    sparkline spans 7 days, so the last 1/7 ≈ the last 24 hours — matching the
    24h change pill so a recent move is visible rather than lost in a week of
    trend."""
    if not points:
        return []
    n = max(2, round(len(points) / fraction))
    return list(points[-n:])


def _downsample(points, target_n):
    if not points:
        return []
    if len(points) <= target_n:
        return list(points)
    stride = len(points) / target_n
    return [points[int(i * stride)] for i in range(target_n)]


# --------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------

def format_price(price):
    if price is None:
        return "$0"
    if price >= 100:
        return f"${price:,.0f}"
    if price >= 1:
        return f"${price:.2f}"
    return f"${price:.4f}"


def format_change(change):
    sign = "+" if change >= 0 else "−"
    return f"{sign}{abs(change):.1f}%"


def _spark_color(spark):
    if not spark or len(spark) < 2:
        return CREMA
    return UP if spark[-1] >= spark[0] else DOWN


# --------------------------------------------------------------------------
# Sparkline renderers
# --------------------------------------------------------------------------

def _svg_sparkline(spark, w=82, h=24):
    if not spark or len(spark) < 2:
        return ""
    pts = list(spark)
    mn, mx = min(pts), max(pts)
    rng = mx - mn or 1
    n = len(pts)
    coords = []
    for i, v in enumerate(pts):
        x = (i / (n - 1)) * (w - 2) + 1
        y = h - 1 - ((v - mn) / rng) * (h - 2)
        coords.append(f"{x:.1f},{y:.1f}")
    color = _spark_color(pts)
    last_x, last_y = coords[-1].split(",")
    return (
        f'<svg class="spark" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" preserveAspectRatio="none">'
        f'<polyline fill="none" stroke="{color}" stroke-width="1.5" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'points="{" ".join(coords)}"/>'
        f'<circle cx="{last_x}" cy="{last_y}" r="1.8" fill="{color}"/>'
        f"</svg>"
    )


def _png_sparkline(spark, ticker):
    """Render a transparent 164x48 PNG via matplotlib. Returns site-relative path."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    SPARKLINES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SPARKLINES_DIR / f"{ticker}.png"
    out_rel = f"/{out_path.as_posix()}"

    pts = list(spark or [])
    if len(pts) < 2:
        # Empty transparent canvas so the email <img> doesn't 404.
        fig = plt.figure(figsize=(1.64, 0.48), dpi=100)
        fig.patch.set_alpha(0)
        fig.savefig(out_path, transparent=True, pad_inches=0)
        plt.close(fig)
        return out_rel

    color = _spark_color(pts)
    fig, ax = plt.subplots(figsize=(1.64, 0.48), dpi=100)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.plot(range(len(pts)), pts, color=color, linewidth=2)
    ax.set_xlim(0, len(pts) - 1)
    ax.set_ylim(min(pts), max(pts))
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(out_path, transparent=True, pad_inches=0)
    plt.close(fig)
    return out_rel


# --------------------------------------------------------------------------
# Strip HTML
# --------------------------------------------------------------------------

def render_strip_html(prices, mode="web"):
    """Render the price strip as an HTML block. Empty string if no prices."""
    if not prices:
        return ""

    chips = []
    for coin in prices:
        ticker = coin["ticker"]
        change = coin.get("change_24h") or 0
        direction = "up" if change >= 0 else "down"

        if mode == "email":
            png_path = _png_sparkline(coin.get("spark") or [], ticker)
            spark_html = (
                f'<img class="spark" '
                f'src="{{{{ "{png_path}" | relative_url }}}}" '
                f'width="82" height="24" alt="">'
            )
        else:
            spark_html = _svg_sparkline(coin.get("spark") or [])

        chips.append(
            f'    <li class="chip">'
            f'<span class="chip-left">'
            f'<span class="ticker">{ticker}</span>'
            f'<span class="price">{format_price(coin.get("price"))}</span>'
            f"</span>"
            f'<span class="chip-right">'
            f'<span class="change {direction}">{format_change(change)}</span>'
            f"{spark_html}"
            f"</span>"
            f"</li>"
        )

    return (
        '<section class="prices">\n'
        '  <p class="prices-label">Prices</p>\n'
        '  <ul class="chips">\n'
        + "\n".join(chips)
        + "\n  </ul>\n"
        "</section>"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    prices = fetch_prices()
    if prices is None:
        print("No prices.")
    else:
        for p in prices:
            print(f"{p['ticker']:5} {format_price(p['price']):>12} {format_change(p['change_24h']):>7} "
                  f"spark={len(p['spark'])}pts")
