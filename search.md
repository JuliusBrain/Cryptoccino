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

    function escHtml(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }

    function render(items) {
      results.innerHTML = items.map(function (it) {
        return '<li class="beat-item"><a href="' + encodeURI(it.url) + '">' +
          '<span class="beat-lead">' + escHtml(it.lead) + '</span>' +
          '<time class="beat-date">' + escHtml(it.beat) + ' · ' + escHtml(it.date) + '</time>' +
          '</a></li>';
      }).join('');
    }

    function run() {
      var q = input.value.trim().toLowerCase();
      if (!q) { results.innerHTML = ''; status.textContent = data.length + ' stories indexed.'; return; }
      var hits = data.filter(function (it) {
        return (it.lead + ' ' + it.text + ' ' + it.beat).toLowerCase().indexOf(q) !== -1;
      });
      status.textContent = hits.length + (hits.length === 1 ? ' match' : ' matches') + ' for “' + q + '”.';
      render(hits);
    }

    fetch('{{ "/search.json" | relative_url }}')
      .then(function (r) { return r.json(); })
      .then(function (j) {
        data = j;
        var pre = new URLSearchParams(location.search).get('q');
        if (pre) input.value = pre;
        run();
        input.focus();
      })
      .catch(function () { status.textContent = 'Search index unavailable.'; });

    input.addEventListener('input', run);
  })();
</script>
