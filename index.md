---
layout: default
---

{% assign latest = site.posts.first %}
{% if latest %}
<article class="issue">
  <header>
    <h1>{{ latest.title }}</h1>
    {% include reading-time.html content=latest.content %}
  </header>
  {{ latest.content }}
</article>
{% else %}
<p class="empty">The first issue lands tomorrow morning.</p>
{% endif %}

{% include subscribe.html variant="cta" %}

{% if site.posts.size > 1 %}
<nav class="archive-link">
  <a href="{{ '/archive/' | relative_url }}">Browse the full archive <span class="arr">→</span></a>
</nav>
{% endif %}
