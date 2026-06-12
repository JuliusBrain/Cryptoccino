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

  /* ---------------- price list (left column) ---------------- */
  function buildPriceList() {
    var ul = $("plist"); if (!ul) return;
    ul.innerHTML = SYMBOLS.map(function (s) {
      return '<li class="tv-prow" id="prow-' + s.d + '">' +
        '<span class="tv-prow__sym">' + s.d + '</span>' +
        '<span class="tv-prow__price" data-num id="pp-' + s.d + '">—</span>' +
        '<span class="tv-prow__chg" data-num id="pc-' + s.d + '">—</span>' +
        '</li>';
    }).join("");
  }
  var flashTimers = {};
  function renderPrice(d) {
    var st = state[d], row = $("prow-" + d), pp = $("pp-" + d), pc = $("pc-" + d);
    if (!row || !pp || !pc) return;
    pp.textContent = fmtPrice(st.price);
    pc.textContent = fmtChg(st.change);
    pc.className = "tv-prow__chg " + dirClass(st.change);
    if (st.prev != null && st.price != null && st.price !== st.prev) {
      var up = st.price > st.prev;
      row.classList.remove("flash-up", "flash-down");
      // reflow so the class re-triggers even on rapid consecutive ticks
      void row.offsetWidth;
      row.classList.add(up ? "flash-up" : "flash-down");
      clearTimeout(flashTimers[d]);
      flashTimers[d] = setTimeout(function () { row.classList.remove("flash-up", "flash-down"); }, 420);
    }
  }

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

  /* ---------------- gainer / loser ---------------- */
  function refreshMovers() {
    var best = null, worst = null;
    SYMBOLS.forEach(function (s) {
      var c = state[s.d].change;
      if (c == null) return;
      if (!best || c > best.c) best = { d: s.d, c: c };
      if (!worst || c < worst.c) worst = { d: s.d, c: c };
    });
    var g = $("m-gain"), l = $("m-lose");
    if (g && best)  g.textContent = best.d + " " + fmtChg(best.c);
    if (l && worst) l.textContent = worst.d + " " + fmtChg(worst.c);
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
        renderPrice(sym.d);
        refreshTicker();
        refreshMovers();
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
          renderPrice(s.d);
        });
        refreshTicker(); refreshMovers();
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
        var mcap = d.total_market_cap && d.total_market_cap.usd;
        if ($("m-dom"))  $("m-dom").textContent  = dom != null ? dom.toFixed(1) + "%" : "—";
        if ($("m-vol"))  $("m-vol").textContent  = fmtCompact(vol);
        if ($("m-mcap")) $("m-mcap").textContent = fmtCompact(mcap);
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

  function renderFng(o) { if ($("m-fng") && o) $("m-fng").textContent = o.value + " · " + o.label.toUpperCase(); }
  function loadFng() {
    var cached = cacheGet("tv-fng", 5 * 60000);
    if (cached) { renderFng(cached); return; }
    fetch("https://api.alternative.me/fng/?limit=1")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var row = j && j.data && j.data[0]; if (!row) throw new Error("no fng");
        var o = { value: row.value, label: row.value_classification };
        cacheSet("tv-fng", o); renderFng(o);
      })
      .catch(function (e) { console.warn("TV: F&G failed", e); });
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
    buildPriceList();
    buildTicker();
    tick(); setInterval(tick, 1000);
    initFullscreen();
    connectWS();
    loadGlobal();   setInterval(loadGlobal, 60000);
    loadFng();      setInterval(loadFng, 5 * 60000);
    loadSecurity(); setInterval(loadSecurity, 30 * 60000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
