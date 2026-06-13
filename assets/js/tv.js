/* Cryptoccino TV — client-side live terminal.
 *
 * No backend. Live data from public, CORS-open, keyless APIs:
 *   prices/ticker : Binance WS (combined miniTicker)  -> CoinGecko REST fallback
 *   charts        : Binance REST klines (BTC 30d) + CoinGecko dominance
 *   market        : CoinGecko /global
 *   sentiment     : alternative.me /fng
 *   derivatives   : Binance futures (funding + open interest)
 *   defi/yields   : DefiLlama
 *   security      : DefiLlama /hacks
 * Every call is wrapped; the static grid renders with "—" placeholders so the
 * page is useful even if a source fails. The data-fetching layer is unchanged
 * from the prior build — only the render layer + layout were rewritten.
 */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  /* Tracked assets: display label + Binance symbol + CoinGecko id. */
  var SYMBOLS = [
    { d: "BTC",  b: "BTCUSDT",  cg: "bitcoin" },
    { d: "ETH",  b: "ETHUSDT",  cg: "ethereum" },
    { d: "SOL",  b: "SOLUSDT",  cg: "solana" },
    { d: "BNB",  b: "BNBUSDT",  cg: "binancecoin" },
    { d: "AVAX", b: "AVAXUSDT", cg: "avalanche-2" },
    { d: "ARB",  b: "ARBUSDT",  cg: "arbitrum" },
    { d: "OP",   b: "OPUSDT",   cg: "optimism" },
    { d: "POL",  b: "POLUSDT",  cg: "matic-network" }
  ];
  var BY_BINANCE = {}, BY_BINANCE_BY_LABEL = {};
  SYMBOLS.forEach(function (s) { BY_BINANCE[s.b] = s; BY_BINANCE_BY_LABEL[s.d] = s; });

  var state = {};   // d -> { price, change, prev }
  SYMBOLS.forEach(function (s) { state[s.d] = { price: null, change: null, prev: null }; });

  /* ---------------- formatting ---------------- */
  function fmtPrice(p) {
    if (p == null || isNaN(p)) return "—";
    var d = p >= 1000 ? 0 : p >= 1 ? 2 : p >= 0.01 ? 4 : 6;
    return "$" + p.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmtChg(c) {
    if (c == null || isNaN(c)) return "—";
    return (c >= 0 ? "+" : "−") + Math.abs(c).toFixed(2) + "%";
  }
  function fmtCompact(n) {
    if (n == null || isNaN(n)) return "—";
    if (n >= 1e12) return "$" + (n / 1e12).toFixed(2) + "T";
    if (n >= 1e9)  return "$" + (n / 1e9).toFixed(2) + "B";
    if (n >= 1e6)  return "$" + (n / 1e6).toFixed(1) + "M";
    return "$" + Math.round(n).toLocaleString("en-US");
  }
  function dirClass(c) { return c == null ? "" : c >= 0 ? "tv-up" : "tv-down"; }

  /* ---------------- clock ---------------- */
  var timeFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Berlin", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
  var dateFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Berlin", weekday: "short", day: "2-digit", month: "short", year: "numeric" });
  function tick() {
    var now = new Date();
    var c = $("clock"); if (c) c.textContent = timeFmt.format(now);
    var d = $("topdate");
    if (d) d.textContent = "CET  " + dateFmt.format(now).toUpperCase().replace(/,/g, ".");
  }

  /* ---------------- ticker (seamless loop) ---------------- */
  function buildTicker() {
    var track = $("track"); if (!track) return;
    // Leading market-direction arrow (BTC 24h as the proxy).
    var btc = state.BTC.change;
    var leadCls = btc == null ? "" : btc >= 0 ? "tv-up" : "tv-down";
    var lead = '<span class="tv-titem__lead ' + leadCls + '">' + (btc == null ? "•" : btc >= 0 ? "▲" : "▼") + '</span>';
    var one = SYMBOLS.map(function (s) {
      var st = state[s.d];
      return '<span class="tv-titem">' +
        '<span class="tv-titem__sym">' + s.d + '</span>' +
        '<span class="tv-titem__price">' + fmtPrice(st.price) + '</span>' +
        '<span class="tv-titem__chg ' + dirClass(st.change) + '">' +
          (st.change == null ? "" : (st.change >= 0 ? "▲" : "▼")) + fmtChg(st.change) +
        '</span></span>';
    }).join("");
    // Duplicate the run so translateX(-50%) lands exactly one copy over -> seamless.
    track.innerHTML = lead + one + lead + one;
    track.style.setProperty("--roll", (SYMBOLS.length * 4.5) + "s");
    track.classList.add("is-rolling");
    stamp("upd-global");
  }
  var tickerThrottle = null;
  function refreshTicker() {
    if (tickerThrottle) return;
    tickerThrottle = setTimeout(function () { tickerThrottle = null; buildTicker(); }, 1500);
  }

  /* ---------------- live status pill ---------------- */
  function setLive(stateName, label) {
    var w = $("livewrap"), l = $("livelabel");
    if (!w || !l) return;
    w.classList.remove("is-live", "is-down");
    if (stateName === "live") w.classList.add("is-live");
    else if (stateName === "down") w.classList.add("is-down");
    l.textContent = label;
  }

  /* ---------------- Binance WS + reconnect ---------------- */
  var ws = null, wsAttempts = 0, WS_MAX = 5, polling = null, gotData = false;
  function wsUrl() {
    var streams = SYMBOLS.map(function (s) { return s.b.toLowerCase() + "@miniTicker"; }).join("/");
    return "wss://stream.binance.com:9443/stream?streams=" + streams;
  }
  function connectWS() {
    try { ws = new WebSocket(wsUrl()); }
    catch (e) { console.warn("TV: WS construct failed", e); return scheduleReconnect(); }

    ws.onopen = function () { wsAttempts = 0; setLive("live", "LIVE"); console.info("TV: Binance WS open"); };
    ws.onmessage = function (ev) {
      try {
        var msg = JSON.parse(ev.data);
        var dta = msg.data || msg;
        var sym = BY_BINANCE[dta.s];
        if (!sym) return;
        var close = parseFloat(dta.c), open = parseFloat(dta.o);
        if (isNaN(close)) return;
        if (!gotData) { gotData = true; console.info("TV: first WS tick", dta.s, dta.c); }
        var st = state[sym.d];
        st.prev = st.price; st.price = close;
        st.change = (open > 0) ? ((close - open) / open) * 100 : st.change;
        refreshTicker();
      } catch (e) { /* ignore a single malformed frame */ }
    };
    ws.onerror = function () { setLive("down", "WS ERROR"); };
    ws.onclose = function () { scheduleReconnect(); };
  }
  function scheduleReconnect() {
    if (polling) return;            // already on the fallback
    if (wsAttempts >= WS_MAX) { console.warn("TV: WS gave up; using CoinGecko polling"); return startPolling(); }
    var delay = Math.min(30000, 1000 * Math.pow(2, wsAttempts));
    wsAttempts++;
    setLive("down", "RECONNECT " + wsAttempts + "/" + WS_MAX);
    setTimeout(connectWS, delay);
  }

  /* ---------------- CoinGecko fallback polling ---------------- */
  function pollPrices() {
    var ids = SYMBOLS.map(function (s) { return s.cg; }).join(",");
    fetch("https://api.coingecko.com/api/v3/simple/price?ids=" + ids + "&vs_currencies=usd&include_24hr_change=true")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        setLive("live", "LIVE · CG");
        SYMBOLS.forEach(function (s) {
          var row = j[s.cg]; if (!row) return;
          var st = state[s.d];
          st.prev = st.price; st.price = row.usd;
          if (row.usd_24h_change != null) st.change = row.usd_24h_change;
        });
        refreshTicker();
      })
      .catch(function (e) { console.warn("TV: CoinGecko poll failed", e); setLive("down", "PRICES DOWN"); });
  }
  function startPolling() {
    if (polling) return;
    pollPrices();
    polling = setInterval(pollPrices, 60000);
  }

  /* ---------------- market metrics (CoinGecko /global) ---------------- */
  function loadGlobal() {
    fetch("https://api.coingecko.com/api/v3/global")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var d = j && j.data; if (!d) throw new Error("no data");
        var dom = d.market_cap_percentage && d.market_cap_percentage.btc;
        var vol = d.total_volume && d.total_volume.usd;
        setText("m-dom", dom != null ? dom.toFixed(1) + "%" : "—");
        setText("m-vol", fmtCompact(vol));
        stamp("upd-market"); stamp("upd-global");
      })
      .catch(function (e) { console.warn("TV: /global failed", e); });
  }

  /* ---------------- cache helper (localStorage, ttl) ---------------- */
  function cacheGet(key, maxAgeMs) {
    try {
      var raw = localStorage.getItem(key); if (!raw) return null;
      var o = JSON.parse(raw);
      if (Date.now() - o.t > maxAgeMs) return null;
      return o.v;
    } catch (e) { return null; }
  }
  function cacheSet(key, v) { try { localStorage.setItem(key, JSON.stringify({ t: Date.now(), v: v })); } catch (e) {} }

  /* ---------------- Fear & Greed (cached 5 min) ---------------- */
  function loadFng() {
    var cached = cacheGet("tv-fng", 5 * 60000);
    if (cached) { LIVE.fearGreed = { value: cached.value, label: cached.label, stale: false }; renderMarket(); return; }
    fetch("https://api.alternative.me/fng/?limit=1")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var row = j && j.data && j.data[0]; if (!row) throw new Error("no fng");
        var o = { value: row.value, label: row.value_classification };
        cacheSet("tv-fng", o);
        LIVE.fearGreed = { value: o.value, label: o.label, stale: false };
        renderMarket();
      })
      .catch(function (e) {
        console.warn("TV: F&G failed", e);
        var last = cacheGet("tv-fng", 7 * 86400000); // last known, up to a week
        if (last) { LIVE.fearGreed = { value: last.value, label: last.label, stale: true }; renderMarket(); }
      });
  }

  /* ---------------- Security (DefiLlama /hacks, cached 30 min) ---------------- */
  function computeSecurity(arr) {
    var now = Date.now() / 1000, DAY = 86400;
    var losses7d = 0, latest = null;
    arr.forEach(function (h) {
      var t = h.date; if (t == null) return;
      if (t >= now - 7 * DAY) losses7d += (h.amount || 0);
      // Only the most recent incident WITHIN 30 days counts as the "last
      // incident"; older than that reads as "None in 30 days".
      if (t >= now - 30 * DAY && (!latest || t > latest.date)) latest = h;
    });
    var state = "clear", label = "ALL CLEAR";
    if (latest) {
      var age = now - latest.date;
      if (age <= DAY)          { state = "active"; label = "ACTIVE INCIDENT"; }
      else if (age <= 7 * DAY) { state = "recent"; label = "RECENT INCIDENT"; }
    }
    var dateStr = latest ? new Date(latest.date * 1000).toLocaleDateString("en-GB", { day: "2-digit", month: "short" }).toUpperCase() : "";
    return { state: state, statusLabel: label, losses7d: losses7d, lastName: latest && latest.name, lastDate: dateStr };
  }
  function loadSecurity() {
    var cached = cacheGet("tv-sec", 30 * 60000);
    if (cached) { renderSecurity(cached); return; }
    fetch("https://api.llama.fi/hacks")
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (arr) {
        if (!Array.isArray(arr)) throw new Error("unexpected shape");
        var o = computeSecurity(arr);
        cacheSet("tv-sec", o); renderSecurity(o);
      })
      .catch(function (e) { console.warn("TV: security failed", e); renderSecurity(null); });
  }

  /* ============================================================
     Central LIVE state; each loader has independent error handling
     and renders only its own section, so one failure never affects
     the others.
     ============================================================ */
  var LIVE = {
    fearGreed: { value: null, label: null, stale: false },
    funding:   { BTC: null, ETH: null, markBTC: null, markETH: null },
    oi:        { BTC: null, ETH: null, btcPrev: null, ethPrev: null },
    defi:      { totalTvl: null, topProtocols: [] },
    stables:   { usdcPct: null, usdtPct: null },
    yields:    { pools: [] },
    digest:    null,
    context:   null
  };

  /* ---- shared helpers ---- */
  function fmtUSD(n) {
    if (n == null || isNaN(n)) return "—";
    var a = Math.abs(n);
    if (a >= 1e12) return "$" + (n / 1e12).toFixed(1) + "T";
    if (a >= 1e9)  return "$" + (n / 1e9).toFixed(2) + "B";
    if (a >= 1e6)  return "$" + (n / 1e6).toFixed(2) + "M";
    if (a >= 1e3)  return "$" + (n / 1e3).toFixed(1) + "K";
    return "$" + Math.round(n);
  }
  function fmtPct(x, dec) { return x == null || isNaN(x) ? "—" : (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(dec == null ? 2 : dec) + "%"; }
  function pctClass(x, band) { band = band == null ? 0.1 : band; return x == null || isNaN(x) ? "" : Math.abs(x) < band ? "tv-amber" : x >= 0 ? "tv-up" : "tv-down"; }
  function escapeHtml(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function truncate(s, n) { s = String(s == null ? "" : s); return s.length > n ? s.slice(0, n) : s; }
  var stampFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Berlin", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
  function stamp(id) { var e = $(id); if (e) e.textContent = stampFmt.format(new Date()); }
  function setText(id, t) { var e = $(id); if (e) e.textContent = t; }
  function setVal(id, t, cls) { var e = $(id); if (!e) return; e.textContent = t; e.className = "tv-row__v" + (cls ? " " + cls : ""); }

  /* ---- MARKET: Fear & Greed + dominance/volume (loadGlobal writes those) ---- */
  function renderMarket() {
    var fg = LIVE.fearGreed;
    setText("m-fng", fg.value == null ? "—" : (fg.value + " · " + (fg.label || "").toUpperCase() + (fg.stale ? " · STALE" : "")));
    var bar = $("fng-bar");
    if (bar && fg.value != null) {
      var v = Math.max(0, Math.min(100, +fg.value));
      bar.style.width = v + "%";
      // 0-25 red · 26-45 orange · 46-55 amber · 56-75 green · 76-100 bright green
      bar.style.background = v <= 25 ? "#E53935" : v <= 45 ? "#E08A2A" : v <= 55 ? "#C8900A" : v <= 75 ? "#4CAF50" : "#7BD17F";
    }
    stamp("upd-market");
  }

  /* ---- DERIVATIVES: Binance futures funding + open interest ---- */
  function loadFunding() {
    fetch("https://fapi.binance.com/fapi/v1/premiumIndex")
      .then(function (r) { return r.json(); })
      .then(function (arr) {
        if (!Array.isArray(arr)) throw new Error("shape");
        ["BTC", "ETH"].forEach(function (k) {
          var row = arr.find(function (x) { return x.symbol === k + "USDT"; });
          if (!row) return;
          LIVE.funding[k] = parseFloat(row.lastFundingRate);
          LIVE.funding["mark" + k] = parseFloat(row.markPrice);
        });
        renderDerivatives();
      })
      .catch(function (e) { console.warn("TV: funding failed", e); renderDerivatives(); });
  }
  function loadOI() {
    ["BTC", "ETH"].forEach(function (k) {
      fetch("https://fapi.binance.com/fapi/v1/openInterest?symbol=" + k + "USDT")
        .then(function (r) { return r.json(); })
        .then(function (j) {
          var contracts = parseFloat(j.openInterest), mark = LIVE.funding["mark" + k];
          if (mark != null && !isNaN(contracts)) { LIVE.oi[k.toLowerCase() + "Prev"] = LIVE.oi[k]; LIVE.oi[k] = contracts * mark; }
          renderDerivatives();
        })
        .catch(function (e) { console.warn("TV: OI " + k + " failed", e); });
    });
  }
  function renderDerivatives() {
    ["BTC", "ETH"].forEach(function (k) {
      var lc = k.toLowerCase(), r = LIVE.funding[k];
      if (r == null) setVal("fund-" + lc, "N/A", "tv-muted");
      else {
        var pct = r * 100, bp = r * 10000;
        var cls = Math.abs(pct) <= 0.005 ? "tv-amber" : pct > 0 ? "tv-up" : "tv-down";
        setVal("fund-" + lc, (pct >= 0 ? "+" : "−") + Math.abs(pct).toFixed(4) + "% · " + (bp >= 0 ? "+" : "−") + Math.abs(bp).toFixed(2) + "bp", cls);
      }
      var oi = LIVE.oi[k], prev = LIVE.oi[lc + "Prev"];
      if (oi == null) setVal("oi-" + lc, "—", null);
      else {
        var dlt = (prev != null && prev > 0) ? ((oi - prev) / prev) * 100 : null;
        setVal("oi-" + lc, fmtUSD(oi) + (dlt != null ? "  " + fmtPct(dlt) : ""), dlt != null ? pctClass(dlt) : null);
      }
    });
    // Interpretation from BOTH funding rates (percent units).
    var b = LIVE.funding.BTC, e = LIVE.funding.ETH, note = "—";
    if (b != null && e != null) {
      var bp = b * 100, ep = e * 100, near = 0.005, strong = 0.02;
      if (Math.abs(bp) < near && Math.abs(ep) < near) note = "Balanced positioning";
      else if (bp > strong && ep > strong)            note = "Leverage heavy — longs paying";
      else if (bp < 0 && ep < 0)                       note = "Shorts dominant — squeeze risk";
      else                                             note = "Diverging sentiment";
    } else if (b != null) {
      note = Math.abs(b * 100) < 0.005 ? "Balanced positioning" : b > 0 ? "Leverage heavy — longs paying" : "Shorts dominant — squeeze risk";
    }
    setText("deriv-note", note);
    stamp("upd-deriv");
  }

  /* ---- DEFI: total TVL + top protocols + stablecoin split ---- */
  function loadDefi() {
    fetch("https://api.llama.fi/v2/historicalChainTvl")
      .then(function (r) { return r.json(); })
      .then(function (arr) { if (Array.isArray(arr) && arr.length) LIVE.defi.totalTvl = arr[arr.length - 1].tvl; renderDeFi(); })
      .catch(function (e) { console.warn("TV: TVL failed", e); });
    fetch("https://api.llama.fi/protocols")
      .then(function (r) { return r.json(); })
      .then(function (arr) {
        if (!Array.isArray(arr)) throw new Error("shape");
        LIVE.defi.topProtocols = arr
          .filter(function (p) { return p.category !== "CEX" && p.tvl != null && p.tvl > 0; })
          .sort(function (a, b) { return b.tvl - a.tvl; })
          .slice(0, 3)
          .map(function (p) { return { name: p.name, tvl: p.tvl, chg: p.change_1d }; });
        renderDeFi();
      })
      .catch(function (e) { console.warn("TV: protocols failed", e); var b = $("defi-prot"); if (b && !LIVE.defi.topProtocols.length) b.innerHTML = '<p class="tv-note">DATA UNAVAILABLE</p>'; });
  }
  function loadStables() {
    fetch("https://stablecoins.llama.fi/stablecoins?includePrices=true")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var assets = j && j.peggedAssets; if (!Array.isArray(assets)) throw new Error("shape");
        var total = 0, usdc = 0, usdt = 0;
        assets.forEach(function (a) {
          if (a.pegType !== "peggedUSD") return;
          var c = a.circulating && a.circulating.peggedUSD; if (c == null) return;
          total += c;
          if (a.symbol === "USDC") usdc += c;
          if (a.symbol === "USDT") usdt += c;
        });
        if (total > 0) { LIVE.stables.usdcPct = usdc / total * 100; LIVE.stables.usdtPct = usdt / total * 100; }
        renderStables();
      })
      .catch(function (e) { console.warn("TV: stables failed", e); var w = $("stb-wrap"); if (w) w.style.display = "none"; });
  }
  function renderDeFi() {
    setText("defi-tvl", fmtUSD(LIVE.defi.totalTvl));
    var box = $("defi-prot");
    if (box && LIVE.defi.topProtocols.length) {
      box.innerHTML = LIVE.defi.topProtocols.map(function (p) {
        // .tv-subrow__name already ellipsis-truncates via CSS; keep the full name.
        return '<div class="tv-subrow"><span class="tv-subrow__name">' + escapeHtml(p.name) + '</span>' +
          '<span class="tv-subrow__v">' + fmtUSD(p.tvl) + '</span>' +
          '<span class="tv-subrow__c ' + pctClass(p.chg) + '">' + (p.chg == null ? "" : fmtPct(p.chg)) + '</span></div>';
      }).join("");
    }
    stamp("upd-defi");
  }
  function renderStables() {
    var s = LIVE.stables;
    if (s.usdcPct == null) return;
    setText("stb-val", "USDC " + s.usdcPct.toFixed(0) + "% · USDT " + s.usdtPct.toFixed(0) + "%");
    var ub = $("stb-usdc-bar"), tb = $("stb-usdt-bar");
    if (ub) ub.style.width = s.usdcPct + "%";
    if (tb) tb.style.width = s.usdtPct + "%";
  }

  /* ---- YIELDS: top filtered pools ---- */
  function loadYields() {
    fetch("https://yields.llama.fi/pools")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var data = j && j.data; if (!Array.isArray(data)) throw new Error("shape");
        LIVE.yields.pools = data
          .filter(function (p) {
            if (!(p.tvlUsd > 1e7)) return false;
            if (!(p.apy > 0 && p.apy < 200)) return false;
            if (p.stablecoin === true && !(p.apy > 8)) return false;
            return true;
          })
          .sort(function (a, b) { return b.apy - a.apy; })
          .slice(0, 3)
          .map(function (p) { return { project: p.project, symbol: p.symbol, apy: p.apy, chain: p.chain }; });
        renderYields();
      })
      .catch(function (e) { console.warn("TV: yields failed", e); var b = $("yields-list"); if (b) b.innerHTML = '<p class="tv-note">DATA UNAVAILABLE</p>'; });
  }
  function renderYields() {
    var box = $("yields-list"); if (!box) return;
    if (!LIVE.yields.pools.length) { box.innerHTML = '<p class="tv-note">NO QUALIFYING POOLS</p>'; stamp("upd-yields"); return; }
    box.innerHTML = LIVE.yields.pools.map(function (p) {
      var pool = (p.project || "") + "·" + (p.symbol || "");   // __name CSS-ellipsis handles width
      var chain = truncate(p.chain, 6);                        // __c is fixed-width, no ellipsis
      return '<div class="tv-subrow"><span class="tv-subrow__name">' + escapeHtml(pool) + '</span>' +
        '<span class="tv-subrow__v tv-up">' + p.apy.toFixed(1) + '%</span>' +
        '<span class="tv-subrow__c">' + escapeHtml(chain) + '</span></div>';
    }).join("");
    stamp("upd-yields");
  }

  /* ---- SECURITY ---- */
  function renderSecurity(o) {
    var light = $("sec-light"), wrap = $("sec-status"), label = $("sec-statuslabel"), losses = $("sec-losses"), last = $("sec-last");
    if (!o) {
      if (label) label.textContent = "DATA UNAVAILABLE";
      if (light) light.setAttribute("data-state", "idle");
      if (wrap) wrap.removeAttribute("data-state");
      stamp("upd-sec"); return;
    }
    if (light) light.setAttribute("data-state", o.state);
    if (wrap)  wrap.setAttribute("data-state", o.state);
    if (label) label.textContent = o.statusLabel;
    if (losses) { losses.textContent = o.losses7d > 0 ? fmtUSD(o.losses7d) : "$0"; losses.className = "tv-row__v" + (o.losses7d > 0 ? " tv-down" : " tv-muted"); }
    if (last) {
      if (o.lastName) { last.textContent = o.lastName + " · " + o.lastDate; last.className = "tv-row__v"; }
      else { last.textContent = "None in 30 days"; last.className = "tv-row__v tv-up"; }
    }
    stamp("upd-sec");
  }

  /* ============================================================
     CENTER CHARTS — two token-selectable 30-day price charts (Binance klines)
     ============================================================ */
  var monDay = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short" });
  function chartErr(id, on) { var e = $(id); if (e) e.hidden = !on; }
  var charts = {};
  function drawChart(canvasId, labels, data, color, fill) {
    if (typeof Chart === "undefined") return false;
    var cv = $(canvasId); if (!cv) return false;
    if (charts[canvasId]) { charts[canvasId].destroy(); }
    charts[canvasId] = new Chart(cv.getContext("2d"), {
      type: "line",
      data: { labels: labels, datasets: [{ data: data, borderColor: color, backgroundColor: fill, fill: true, borderWidth: 1.5 }] },
      options: {
        responsive: true, maintainAspectRatio: false, animation: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: { x: { display: false }, y: { display: false } },
        elements: { point: { radius: 0 }, line: { tension: 0.3 } }
      }
    });
    return true;
  }
  // Two chart slots; each shows the selected token's 30-day price. Slot A defaults
  // to BTC (amber), slot B to ETH (blue); the picker persists per slot.
  var chartSel = { a: "BTC", b: "ETH" };
  var CHART_COLOR = { a: ["#C8900A", "rgba(200,144,10,0.08)"], b: ["#5A7A9A", "rgba(90,122,154,0.08)"] };
  function binanceSymbol(d) { var s = BY_BINANCE_BY_LABEL[d]; return s ? s.b : (d + "USDT"); }
  function loadChart(slot) {
    var sym = chartSel[slot], canvasId = "chart-" + slot, errId = "chart-" + slot + "-err";
    setText("chart-" + slot + "-title", sym + " / USD · 30 Day");
    chartErr(errId, false);
    fetch("https://api.binance.com/api/v3/klines?symbol=" + binanceSymbol(sym) + "&interval=1d&limit=30")
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (rows) {
        if (!Array.isArray(rows) || !rows.length) throw new Error("shape");
        var labels = rows.map(function (k) { return monDay.format(new Date(k[0])); });
        var data = rows.map(function (k) { return parseFloat(k[4]); });
        if (!drawChart(canvasId, labels, data, CHART_COLOR[slot][0], CHART_COLOR[slot][1])) throw new Error("no Chart.js");
      })
      .catch(function (e) { console.warn("TV: chart " + slot + " (" + sym + ") failed", e); chartErr(errId, true); });
  }
  function renderCenterCharts() { loadChart("a"); loadChart("b"); }
  function initChartPickers() {
    ["a", "b"].forEach(function (slot) {
      var saved = null; try { saved = localStorage.getItem("tv-chart-" + slot); } catch (e) {}
      if (saved && BY_BINANCE_BY_LABEL[saved]) chartSel[slot] = saved;
      var sel = $("chart-" + slot + "-sym"); if (!sel) return;
      sel.value = chartSel[slot];
      sel.addEventListener("change", function () {
        if (!BY_BINANCE_BY_LABEL[sel.value]) return;
        chartSel[slot] = sel.value;
        try { localStorage.setItem("tv-chart-" + slot, sel.value); } catch (e) {}
        loadChart(slot);
      });
    });
  }

  /* ============================================================
     NEWS DIGEST — Haiku-deduped headlines (news_digest.json, news-data branch).
     Headlines/takes/sources are untrusted → escaped; links validated to http(s).
     ============================================================ */
  var DIGEST_URL = "https://raw.githubusercontent.com/JuliusBrain/Cryptoccino/news-data/news_digest.json";
  var DIGEST_CATS = [["market", "MARKET"], ["business", "BUSINESS"], ["security", "SECURITY"], ["policy", "POLICY"]];
  function loadDigest() {
    fetch(DIGEST_URL + "?t=" + Math.floor(Date.now() / 300000))   // bust raw's ~5-min cache
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (o) { LIVE.digest = o; renderDigest(); })
      .catch(function (e) { console.warn("TV: digest failed", e); renderDigest(); });
  }
  function renderDigest() {
    var box = $("digest-list"); if (!box) return;
    var d = LIVE.digest;
    if (!d) { box.innerHTML = '<li class="tv-dg__empty">No digest yet.</li>'; return; }
    var html = "";
    DIGEST_CATS.forEach(function (c) {
      var items = d[c[0]] || [];
      if (!items.length) return;
      html += '<li class="tv-dg__cat tv-dg__cat--' + c[0] + '">' + c[1] + '</li>';
      items.forEach(function (s) {
        var href = /^https?:\/\//.test(s.link || "") ? s.link : "#";
        html += '<li class="tv-dg__item"><a href="' + escapeHtml(href) + '" target="_blank" rel="noopener noreferrer">' +
          '<span class="tv-dg__head">' + escapeHtml(s.headline) + '</span>' +
          (s.take ? '<span class="tv-dg__take">' + escapeHtml(s.take) + '</span>' : '') +
          '<span class="tv-dg__src">' + escapeHtml(s.source) + '</span></a></li>';
      });
    });
    box.innerHTML = html || '<li class="tv-dg__empty">No digest yet.</li>';
    stamp("upd-digest");
  }

  /* ============================================================
     MARKET CONTEXT — Claude blurb (context.json, news-data branch); hide if none.
     ============================================================ */
  var CONTEXT_URL = "https://raw.githubusercontent.com/JuliusBrain/Cryptoccino/news-data/context.json";
  function loadContext() {
    fetch(CONTEXT_URL + "?t=" + Math.floor(Date.now() / 300000))
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (o) { LIVE.context = o; renderContext(); })
      .catch(function (e) { console.warn("TV: context failed", e); renderContext(); });
  }
  function renderContext() {
    var sec = $("market-context"); if (!sec) return;
    var t = LIVE.context && LIVE.context.text;
    if (!t) { sec.hidden = true; return; }            // not generated yet → hide
    setText("context-summary", t);                    // textContent — no innerHTML
    sec.hidden = false;
    stamp("upd-context");
  }

  /* ---------------- theme toggle (dark ↔ Latte, persisted) ---------------- */
  function initTheme() {
    var btn = $("themebtn"); if (!btn) return;
    var root = document.documentElement;
    function syncLabel() {
      // Label names the theme you'll switch TO.
      btn.textContent = root.getAttribute("data-theme") === "latte" ? "DARK" : "LATTE";
    }
    syncLabel();   // the layout head already applied any saved theme pre-paint
    btn.addEventListener("click", function () {
      var toLatte = root.getAttribute("data-theme") !== "latte";
      if (toLatte) root.setAttribute("data-theme", "latte");
      else root.removeAttribute("data-theme");
      try { localStorage.setItem("tv-theme", toLatte ? "latte" : "dark"); } catch (e) {}
      syncLabel();
    });
  }

  /* ---------------- fullscreen ---------------- */
  function initFullscreen() {
    var btn = $("fsbtn"); if (!btn) return;
    btn.addEventListener("click", function () {
      var root = document.documentElement;
      if (!document.fullscreenElement) { (root.requestFullscreen || function () {}).call(root); }
      else { (document.exitFullscreen || function () {}).call(document); }
    });
  }

  /* ---------------- help tooltips (custom, viewport-positioned) ---------------- */
  var tipEl = null;
  function showTip(el) {
    var text = el.getAttribute("data-tip"); if (!text) return;
    if (!tipEl) { tipEl = document.createElement("div"); tipEl.className = "tv-tip"; tipEl.setAttribute("role", "tooltip"); document.body.appendChild(tipEl); }
    tipEl.textContent = text;
    tipEl.style.display = "block";
    var r = el.getBoundingClientRect(), tw = tipEl.offsetWidth, th = tipEl.offsetHeight;
    var vw = window.innerWidth, vh = window.innerHeight, pad = 8;
    var left = r.right - tw;                       // right-align to the badge (sidebar sits at the right edge)
    if (left < pad) left = pad;
    if (left + tw > vw - pad) left = vw - pad - tw;
    var top = r.bottom + 8;                         // below the badge by default
    if (top + th > vh - pad) top = r.top - th - 8;  // flip above if no room below
    if (top < pad) top = pad;
    tipEl.style.left = left + "px";
    tipEl.style.top = top + "px";
  }
  function hideTip() { if (tipEl) tipEl.style.display = "none"; }
  function initTips() {
    function find(e) { return e.target && e.target.closest ? e.target.closest("[data-tip]") : null; }
    document.addEventListener("mouseover", function (e) { var el = find(e); if (el) showTip(el); });
    document.addEventListener("mouseout",  function (e) { if (find(e)) hideTip(); });
    document.addEventListener("focusin",   function (e) { var el = find(e); if (el) showTip(el); });
    document.addEventListener("focusout",  hideTip);
  }

  /* ---------------- init ---------------- */
  function init() {
    // Chart.js global defaults (once).
    if (typeof Chart !== "undefined") {
      Chart.defaults.color = "#3E3830";
      Chart.defaults.borderColor = "#1C2028";
      Chart.defaults.font.family = "'JetBrains Mono', monospace";
      Chart.defaults.font.size = 9;
    }

    buildTicker();
    tick(); setInterval(tick, 1000);
    initTheme();
    initFullscreen();
    initChartPickers();
    initTips();
    connectWS();
    // paint section structure with placeholders
    renderMarket(); renderDerivatives(); renderDeFi(); renderYields();

    // Stagger the initial burst by 200ms each.
    var loaders = [loadDigest, loadContext, loadFng, loadGlobal, loadFunding, loadOI, loadDefi, loadStables, loadYields, loadSecurity, renderCenterCharts];
    loaders.forEach(function (fn, i) { setTimeout(fn, i * 200); });

    setInterval(loadDigest, 30 * 60000);
    setInterval(loadContext, 30 * 60000);
    setInterval(loadFng, 5 * 60000);
    setInterval(loadGlobal, 60000);
    setInterval(loadFunding, 60000);
    setInterval(loadOI, 120000);
    setInterval(loadDefi, 10 * 60000);
    setInterval(loadStables, 15 * 60000);
    setInterval(loadYields, 15 * 60000);
    setInterval(loadSecurity, 30 * 60000);
    setInterval(renderCenterCharts, 30 * 60000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
