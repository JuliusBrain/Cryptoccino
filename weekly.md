---
layout: default
title: "Weekly Recap — Cryptoccino"
description: "The week's biggest crypto stories, recapped — freshest first."
permalink: /weekly/
---

<section class="archive-page">
  <header class="archive-head">
    <p class="archive-eyebrow">● The week in review</p>
    <h1>Weekly Recap</h1>
    <p class="archive-sub">The biggest stories of each week, freshest first.</p>
  </header>

  {% assign recaps = site.weekly | sort: "date" | reverse %}
  {% if recaps.size > 0 %}
  <ul class="archive-grid">
    {% for recap in recaps %}
      <li class="archive-card">
        <a href="{{ recap.url | relative_url }}">
          <time class="archive-date" datetime="{{ recap.date | date_to_xmlschema }}">
            <span class="ad-day">{{ recap.date | date: "%-d" }}</span>
            <span class="ad-rest">
              <span class="ad-dow">{{ recap.date | date: "%a" }}</span>
              <span class="ad-my">{{ recap.date | date: "%b %Y" }}</span>
            </span>
          </time>
          {% if recap.description %}<p class="archive-pour">{{ recap.description | strip_html | truncate: 160 | escape }}</p>{% endif %}
          <span class="archive-cta">Read recap <span class="arr">→</span></span>
        </a>
      </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="empty">The first weekly recap lands this weekend.</p>
  {% endif %}
</section>
