/* Cryptoccino TV — client-side live terminal.
 *
 * No backend, no build step. Live data from public, CORS-open, keyless APIs:
 *   prices/ticker : Binance WS (combined miniTicker)  -> CoinGecko REST fallback
 *   market        : CoinGecko /global
 *   sentiment     : alternative.me /fng
 *   security      : DefiLlama /hacks
 * Every call is wrapped; the static grid renders with "—" placeholders so the
 * page is useful even if a source fails.
 */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  /* Tracked assets: display label + Binance symbol + CoinGecko id.
     (MATIC migrated to POL on Binance; shown as POL with the matic-network id.) */
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
  var BY_BINANCE = {}, BY_CG = {};
  SYMBOLS.forEach(function (s) { BY_BINANCE[s.b] = s; BY_CG[s.cg] = s; });

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
    var d = $("topdate"); if (d) d.textContent = dateFmt.format(now).toUpperCase();
  }

  /* Prices feed the bottom ticker only (the left column now holds the digest). */

  /* ---------------- ticker (seamless loop) ---------------- */
  function buildTicker() {
    var track = $("track"); if (!track) return;
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
    track.innerHTML = one + one;
    track.style.setProperty("--roll", (SYMBOLS.length * 4.5) + "s");
    track.classList.add("is-rolling");
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
        if ($("m-dom")) $("m-dom").textContent = dom != null ? dom.toFixed(1) + "%" : "—";
        if ($("m-vol")) $("m-vol").textContent = fmtCompact(vol);
        stamp("upd-market");
      })
      .catch(function (e) { console.warn("TV: /global failed", e); });
  }

  /* ---------------- Fear & Greed (cached 5 min) ---------------- */
  function cacheGet(key, maxAgeMs) {
    try {
      var raw = localStorage.getItem(key); if (!raw) return null;
      var o = JSON.parse(raw);
      if (Date.now() - o.t > maxAgeMs) return null;
      return o.v;
    } catch (e) { return null; }
  }
  function cacheSet(key, v) { try { localStorage.setItem(key, JSON.stringify({ t: Date.now(), v: v })); } catch (e) {} }

  function loadFng() {
    var cached = cacheGet("tv-fng", 5 * 60000);
    if (cached) { LIVE.fearGreed = { value: cached.value, label: cached.label, stale: false }; renderFearGreed(); return; }
    fetch("https://api.alternative.me/fng/?limit=1")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var row = j && j.data && j.data[0]; if (!row) throw new Error("no fng");
        var o = { value: row.value, label: row.value_classification };
        cacheSet("tv-fng", o);
        LIVE.fearGreed = { value: o.value, label: o.label, stale: false };
        renderFearGreed();
      })
      .catch(function (e) {
        console.warn("TV: F&G failed", e);
        var last = cacheGet("tv-fng", 7 * 86400000); // last known, up to a week
        if (last) { LIVE.fearGreed = { value: last.value, label: last.label, stale: true }; renderFearGreed(); }
      });
  }

  /* ---------------- Security (DefiLlama /hacks, cached 30 min) ---------------- */
  function renderSecurity(o) {
    var light = $("sec-light"), status = $("sec-status"), losses = $("sec-losses"), last = $("sec-last");
    if (!o) { if (status) { status.textContent = "DATA UNAVAILABLE"; status.removeAttribute("data-state"); } if (light) light.setAttribute("data-state", "idle"); return; }
    if (light)  light.setAttribute("data-state", o.state);
    if (status) { status.textContent = o.statusLabel; status.setAttribute("data-state", o.state); }
    if (losses) losses.textContent = fmtCompact(o.losses7d);
    if (last)   last.textContent = o.lastName ? (o.lastName + " · " + o.lastDate) : "—";
  }
  function computeSecurity(arr) {
    var now = Date.now() / 1000, DAY = 86400;
    var losses7d = 0, latest = null;
    arr.forEach(function (h) {
      var t = h.date; if (t == null) return;
      if (t >= now - 7 * DAY) losses7d += (h.amount || 0);
      if (!latest || t > latest.date) latest = h;
    });
    var state = "clear", label = "ALL CLEAR";
    if (latest) {
      var age = now - latest.date;
      if (age <= DAY)       { state = "active"; label = "ACTIVE"; }
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
        console.info("TV: hacks rows", arr.length);
        var o = computeSecurity(arr);
        cacheSet("tv-sec", o); renderSecurity(o);
      })
      .catch(function (e) { console.warn("TV: security failed", e); renderSecurity(null); });
  }

  /* ============================================================
     Extended sidebar data sources. Central LIVE state; each loader
     has independent error handling and renders only its own section,
     so one failure never affects the others.
     ============================================================ */
  var LIVE = {
    fearGreed: { value: null, label: null, stale: false },
    funding:   { BTC: null, ETH: null, markBTC: null, markETH: null },
    oi:        { BTC: null, ETH: null, btcPrev: null, ethPrev: null },
    defi:      { totalTvl: null, topProtocols: [] },
    stables:   { usdcPct: null, usdtPct: null },
    yields:    { pools: [] },
    unlocks:   { events: [] },
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
  var stampFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Berlin", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
  function stamp(id) { var e = $(id); if (e) e.textContent = stampFmt.format(new Date()); }
  function setText(id, t) { var e = $(id); if (e) e.textContent = t; }
  function setVal(id, t, cls) { var e = $(id); if (!e) return; e.textContent = t; e.className = "tv-row__v mono" + (cls ? " " + cls : ""); }

  /* ---- MARKET: Fear & Greed (loadFng above writes LIVE then calls this) ---- */
  function renderFearGreed() {
    var fg = LIVE.fearGreed;
    setText("m-fng", fg.value == null ? "—" : (fg.value + " · " + (fg.label || "").toUpperCase() + (fg.stale ? " · STALE" : "")));
    var bar = $("fng-bar");
    if (bar && fg.value != null) {
      var v = Math.max(0, Math.min(100, +fg.value));
      bar.style.width = v + "%";
      bar.style.background = v <= 25 ? "var(--down)" : v <= 45 ? "var(--amber)" : v <= 55 ? "var(--muted)" : v <= 75 ? "var(--up)" : "var(--cyan)";
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
        renderDerivs();
      })
      .catch(function (e) { console.warn("TV: funding failed", e); renderDerivs(); });
  }
  function loadOI() {
    ["BTC", "ETH"].forEach(function (k) {
      fetch("https://fapi.binance.com/fapi/v1/openInterest?symbol=" + k + "USDT")
        .then(function (r) { return r.json(); })
        .then(function (j) {
          var contracts = parseFloat(j.openInterest), mark = LIVE.funding["mark" + k];
          if (mark != null && !isNaN(contracts)) { LIVE.oi[k.toLowerCase() + "Prev"] = LIVE.oi[k]; LIVE.oi[k] = contracts * mark; }
          renderDerivs();
        })
        .catch(function (e) { console.warn("TV: OI " + k + " failed", e); });
    });
  }
  function renderDerivs() {
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
    var note = "—";
    if (LIVE.funding.BTC != null) {
      var p = LIVE.funding.BTC * 100;
      note = Math.abs(p) <= 0.005 ? "Funding flat — leverage balanced."
        : p > 0 ? "Positive funding — longs pay, leveraged bullish."
        : "Negative funding — shorts pay, fear / squeeze risk.";
    }
    setText("deriv-note", note);
    stamp("upd-deriv");
  }

  /* ---- DEFI: total TVL + top protocols ---- */
  function loadDefi() {
    fetch("https://api.llama.fi/v2/historicalChainTvl")
      .then(function (r) { return r.json(); })
      .then(function (arr) { if (Array.isArray(arr) && arr.length) LIVE.defi.totalTvl = arr[arr.length - 1].tvl; renderDefi(); })
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
        renderDefi();
      })
      .catch(function (e) { console.warn("TV: protocols failed", e); var b = $("defi-prot"); if (b && !LIVE.defi.topProtocols.length) b.innerHTML = '<p class="tv-note mono">DATA UNAVAILABLE</p>'; });
  }
  function renderDefi() {
    setText("defi-tvl", fmtUSD(LIVE.defi.totalTvl));
    var box = $("defi-prot");
    if (box && LIVE.defi.topProtocols.length) {
      box.innerHTML = LIVE.defi.topProtocols.map(function (p) {
        return '<div class="tv-subrow"><span class="tv-subrow__name">' + escapeHtml(p.name) + '</span>' +
          '<span class="tv-subrow__v mono">' + fmtUSD(p.tvl) + '</span>' +
          '<span class="tv-subrow__c mono ' + pctClass(p.chg) + '">' + (p.chg == null ? "" : fmtPct(p.chg)) + '</span></div>';
      }).join("");
    }
    stamp("upd-defi");
  }

  /* ---- DEFI: stablecoin dominance ---- */
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
      .catch(function (e) { console.warn("TV: yields failed", e); var b = $("yields-list"); if (b) b.innerHTML = '<p class="tv-note mono">DATA UNAVAILABLE</p>'; });
  }
  function renderYields() {
    var box = $("yields-list"); if (!box) return;
    if (!LIVE.yields.pools.length) { box.innerHTML = '<p class="tv-note mono">NO QUALIFYING POOLS</p>'; stamp("upd-yields"); return; }
    box.innerHTML = LIVE.yields.pools.map(function (p) {
      return '<div class="tv-subrow"><span class="tv-subrow__name">' + escapeHtml(p.project) + ' · ' + escapeHtml(p.symbol) + '</span>' +
        '<span class="tv-subrow__v mono tv-up">' + p.apy.toFixed(1) + '%</span>' +
        '<span class="tv-subrow__c mono">' + escapeHtml(p.chain) + '</span></div>';
    }).join("");
    stamp("upd-yields");
  }

  /* ---- UNLOCKS STRIP (no free aggregate source today; degrades to hidden) ---- */
  function loadUnlocks() {
    fetch("https://api.llama.fi/unlocks")
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (arr) {
        if (!Array.isArray(arr)) throw new Error("shape");
        var now = Date.now(), wk = now + 7 * 86400000;
        LIVE.unlocks.events = arr
          .map(function (u) { return { symbol: u.symbol, value: u.unlockValue, t: u.timestamp > 1e12 ? u.timestamp : u.timestamp * 1000 }; })
          .filter(function (u) { return u.t >= now && u.t <= wk; })
          .sort(function (a, b) { return a.t - b.t; });
        renderUnlocksStrip();
      })
      .catch(function (e) { console.info("TV: unlocks source unavailable (free tier) —", e.message); renderUnlocksStrip(); });
  }
  function renderUnlocksStrip() {
    var strip = $("unlocks"), track = $("unlocks-track"), ev = LIVE.unlocks.events;
    if (!strip || !track || !ev || !ev.length) { if (strip) strip.hidden = true; return; }
    var now = Date.now();
    var html = ev.map(function (u) {
      var ms = u.t - now, d = Math.floor(ms / 86400000), h = Math.floor((ms % 86400000) / 3600000), mm = (u.value || 0) / 1e6;
      var cls = mm < 10 ? "uk-sm" : mm <= 50 ? "uk-md" : "uk-lg";
      return '<span class="tv-uk ' + cls + '"><b>' + escapeHtml(u.symbol) + '</b> $' + mm.toFixed(1) + 'M unlock in ' + d + 'd ' + h + 'h</span>';
    }).join("");
    track.innerHTML = html + html;
    track.style.setProperty("--roll", Math.max(40, ev.length * 8) + "s");
    track.classList.add("is-rolling");
    strip.hidden = false;
  }

  /* ---- NEWS DIGEST: Claude-curated, deduped, categorized headlines ----
     Built every ~3h (pipeline/news_digest.py) and published to the news-data
     branch; fetched off raw.githubusercontent.com (CORS-open, ~5min cache).
     Headlines/takes/sources are untrusted → all escaped; links validated. */
  var DIGEST_URL = "https://raw.githubusercontent.com/JuliusBrain/Cryptoccino/news-data/news_digest.json";
  var DIGEST_CATS = [["market", "MARKET"], ["business", "BUSINESS"], ["security", "SECURITY"], ["policy", "POLICY"]];
  function loadDigest() {
    fetch(DIGEST_URL + "?t=" + Math.floor(Date.now() / 300000))   // bust raw's 5-min cache
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (o) { LIVE.digest = o; renderDigest(); })
      .catch(function (e) { console.warn("TV: digest failed", e); renderDigest(); });
  }
  function renderDigest() {
    var box = $("digest-list"); if (!box) return;
    var d = LIVE.digest;
    if (!d) { box.innerHTML = '<li class="tv-dg__empty mono">No digest yet.</li>'; return; }
    var html = "";
    DIGEST_CATS.forEach(function (c) {
      var items = d[c[0]] || [];
      if (!items.length) return;
      html += '<li class="tv-dg__cat mono">' + c[1] + '</li>';
      items.forEach(function (s) {
        var href = /^https?:\/\//.test(s.link || "") ? s.link : "#";
        html += '<li class="tv-dg__item"><a href="' + escapeHtml(href) + '" target="_blank" rel="noopener noreferrer">' +
          '<span class="tv-dg__head">' + escapeHtml(s.headline) + '</span>' +
          (s.take ? '<span class="tv-dg__take">' + escapeHtml(s.take) + '</span>' : '') +
          '<span class="tv-dg__src mono">' + escapeHtml(s.source) + '</span></a></li>';
      });
    });
    box.innerHTML = html || '<li class="tv-dg__empty mono">No digest yet.</li>';
    stamp("upd-digest");
  }

  /* ---- MARKET CONTEXT: Claude-written blurb off the news-data branch ---- */
  var CONTEXT_URL = "https://raw.githubusercontent.com/JuliusBrain/Cryptoccino/news-data/context.json";
  function loadContext() {
    fetch(CONTEXT_URL + "?t=" + Math.floor(Date.now() / 300000))   // bust raw's 5-min cache
      .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function (o) { LIVE.context = o; renderContext(); })
      .catch(function (e) { console.warn("TV: context failed", e); renderContext(); });
  }
  function renderContext() {
    var box = $("context-body"); if (!box) return;
    var t = LIVE.context && LIVE.context.text;
    box.textContent = t ? t : "No market context.";   // textContent escapes — no innerHTML
    if (t) stamp("upd-context");
  }

  /* ---- render-all dispatcher (spec API; used to paint placeholders on load) ---- */
  function renderRightColumn() { renderFearGreed(); renderDerivs(); renderDefi(); renderStables(); renderYields(); }

  /* ---------------- fullscreen ---------------- */
  function initFullscreen() {
    var btn = $("fsbtn"); if (!btn) return;
    btn.addEventListener("click", function () {
      var root = document.documentElement;
      if (!document.fullscreenElement) { (root.requestFullscreen || function () {}).call(root); }
      else { (document.exitFullscreen || function () {}).call(document); }
    });
  }

  /* ---------------- init ---------------- */
  function init() {
    buildTicker();
    tick(); setInterval(tick, 1000);
    initFullscreen();
    connectWS();
    renderRightColumn();   // paint section structure with placeholders

    // Stagger the initial burst by 200ms each.
    var loaders = [loadDigest, loadContext, loadFng, loadGlobal, loadFunding, loadOI, loadDefi, loadStables, loadYields, loadUnlocks, loadSecurity];
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
    setInterval(loadUnlocks, 30 * 60000);
    setInterval(loadSecurity, 30 * 60000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
