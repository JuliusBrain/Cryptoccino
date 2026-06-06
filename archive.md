---
layout: default
title: "Archive — Cryptoccino"
description: "Every Cryptoccino issue, freshest first."
permalink: /archive/
---

<section class="archive-page">
  <header class="archive-head">
    <p class="archive-eyebrow">● The back bar</p>
    <h1>Archive</h1>
    <p class="archive-sub">Every issue, freshest first.</p>
  </header>

  {% if site.posts.size > 0 %}
  <ul class="archive-grid">
    {% for post in site.posts %}
      <li class="archive-card">
        <a href="{{ post.url | relative_url }}">
          <time class="archive-date" datetime="{{ post.date | date_to_xmlschema }}">
            <span class="ad-day">{{ post.date | date: "%-d" }}</span>
            <span class="ad-rest">
              <span class="ad-dow">{{ post.date | date: "%a" }}</span>
              <span class="ad-my">{{ post.date | date: "%b %Y" }}</span>
            </span>
          </time>
          {% if post.description %}<p class="archive-pour">{{ post.description | strip_html | truncate: 160 }}</p>{% endif %}
          <span class="archive-cta">Read issue <span class="arr">→</span></span>
        </a>
      </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="empty">The first issue lands tomorrow morning.</p>
  {% endif %}
</section>
