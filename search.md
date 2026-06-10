---
layout: default
title: "Search — Cryptoccino"
description: "Search every Cryptoccino story."
permalink: /search/
---
<section class="search-page">
  <header class="archive-head">
    <p class="archive-eyebrow">● Search</p>
    <h1>Search</h1>
    <p class="archive-sub">Find a story across every issue.</p>
  </header>
  <form class="search-form" role="search" onsubmit="return false">
    <input type="search" id="q" class="search-input" autocomplete="off"
           placeholder="coin, project, event…" aria-label="Search stories">
  </form>
  <p class="search-status" id="search-status" aria-live="polite">Loading the index…</p>
  <ul class="beat-list" id="search-results"></ul>
</section>

<script>
  (function () {
    var input = document.getElementById('q');
    var status = document.getElementById('search-status');
    var results = document.getElementById('search-results');
    var data = [];

    var MAX_RESULTS = 50;       // cap the DOM; status reports the true total
    var SNIPPET_LEN = 160;      // chars of matched context to show
    var FUZZY_MIN_LEN = 4;      // only typo-tolerate terms this long
    var FUZZY_TRIGGER = 3;      // run the fuzzy pass only when strict yields < this

    function escHtml(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }
    function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

    // True if `a` is within Levenshtein distance 1 of `b` (early-exit, bounded).
    function near(a, b) {
      if (a === b) return true;
      var la = a.length, lb = b.length;
      if (Math.abs(la - lb) > 1) return false;
      var i = 0, j = 0, edits = 0;
      while (i < la && j < lb) {
        if (a[i] === b[j]) { i++; j++; continue; }
        if (++edits > 1) return false;
        if (la > lb) i++; else if (lb > la) j++; else { i++; j++; }
      }
      return edits + (la - i) + (lb - j) <= 1;
    }

    // Wrap exact term occurrences in <mark>. Input is RAW text: escape first,
    // then insert only literal <mark> tags, so highlighting can't inject HTML.
    function highlight(raw, terms) {
      var out = escHtml(raw);
      terms.forEach(function (t) {
        if (!t) return;
        out = out.replace(new RegExp('(' + escRe(escHtml(t)) + ')', 'gi'), '<mark>$1</mark>');
      });
      return out;
    }

    // ~SNIPPET_LEN window of `text` around the first term hit, with ellipses.
    function snippet(text, terms) {
      if (!text) return '';
      var low = text.toLowerCase(), at = -1;
      for (var i = 0; i < terms.length; i++) {
        var p = low.indexOf(terms[i]);
        if (p !== -1 && (at === -1 || p < at)) at = p;
      }
      if (at === -1) return text.length > SNIPPET_LEN ? text.slice(0, SNIPPET_LEN) + '…' : text;
      var start = Math.max(0, at - 40), end = Math.min(text.length, start + SNIPPET_LEN);
      return (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
    }

    // Score one entry against the query terms. Returns -1 if any term is unmet
    // (AND). `fuzzy` enables the Levenshtein fallback per term.
    function score(it, terms, phrase, fuzzy) {
      var total = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i], s = 0;
        if (it._lead.indexOf(t) !== -1) s = 10;
        else if (it._beat.indexOf(t) !== -1) s = 6;
        else if (it._text.indexOf(t) !== -1) s = 3;
        else if (fuzzy && t.length >= FUZZY_MIN_LEN) {
          for (var k = 0; k < it._tokens.length; k++) { if (near(t, it._tokens[k])) { s = 1; break; } }
        }
        if (s === 0) return -1;
        total += s;
      }
      if (phrase && it._hay.indexOf(phrase) !== -1) total += 8;  // contiguous-phrase bonus
      return total;
    }

    function search(q) {
      var terms = q.split(/\s+/).filter(Boolean);
      if (!terms.length) return [];
      var hits = [];
      // Strict pass first (fast). Fall back to fuzzy only if it under-delivers.
      for (var pass = 0; pass < 2; pass++) {
        var fuzzy = pass === 1;
        hits = [];
        for (var i = 0; i < data.length; i++) {
          var sc = score(data[i], terms, q, fuzzy);
          if (sc >= 0) hits.push({ it: data[i], sc: sc, ord: i });
        }
        if (!fuzzy && hits.length >= FUZZY_TRIGGER) break;
        if (fuzzy) break;
        if (hits.length >= FUZZY_TRIGGER) break;
      }
      // Stable: higher score first, original (newest-first) order as tiebreak.
      hits.sort(function (a, b) { return b.sc - a.sc || a.ord - b.ord; });
      return hits.map(function (h) { return h.it; }).concat();
    }

    function render(items, terms) {
      results.innerHTML = items.slice(0, MAX_RESULTS).map(function (it) {
        return '<li class="beat-item"><a href="' + encodeURI(it.url) + '">' +
          '<span class="beat-main">' +
            '<span class="beat-lead">' + highlight(it.lead, terms) + '</span>' +
            '<span class="beat-snippet">' + highlight(snippet(it.text, terms), terms) + '</span>' +
          '</span>' +
          '<time class="beat-date">' + escHtml(it.beat) + ' · ' + escHtml(it.date) + '</time>' +
          '</a></li>';
      }).join('');
    }

    function run() {
      var q = input.value.trim().toLowerCase();
      if (!q) { results.innerHTML = ''; status.textContent = data.length + ' stories indexed.'; return; }
      var terms = q.split(/\s+/).filter(Boolean);
      var hits = search(q);
      var n = hits.length;
      var shown = Math.min(n, MAX_RESULTS);
      status.textContent = n
        ? n + (n === 1 ? ' match' : ' matches') + ' for “' + q + '”' + (n > shown ? ' — showing top ' + shown : '') + '.'
        : 'No matches for “' + q + '”.';
      render(hits, terms);
    }

    // Debounce keystrokes so the (occasionally fuzzy) pass doesn't run per char.
    var timer;
    function schedule() { clearTimeout(timer); timer = setTimeout(run, 120); }

    fetch('{{ "/search.json" | relative_url }}')
      .then(function (r) { return r.json(); })
      .then(function (j) {
        // Precompute lowercased fields + a token list once, not per keystroke.
        data = j.map(function (it) {
          var lead = it.lead || '', text = it.text || '', beat = it.beat || '';
          return {
            url: it.url, date: it.date, beat: beat, lead: lead, text: text,
            _lead: lead.toLowerCase(), _text: text.toLowerCase(), _beat: beat.toLowerCase(),
            _hay: (lead + ' ' + text + ' ' + beat).toLowerCase(),
            _tokens: (lead + ' ' + text).toLowerCase().split(/[^a-z0-9]+/).filter(Boolean)
          };
        });
        var pre = new URLSearchParams(location.search).get('q');
        if (pre) input.value = pre;
        run();
        input.focus();
      })
      .catch(function () { status.textContent = 'Search index unavailable.'; });

    input.addEventListener('input', schedule);
  })();
</script>
