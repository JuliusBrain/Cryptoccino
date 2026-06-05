---
layout: default
---

{% assign latest = site.posts.first %}
{% if latest %}
<article class="issue">
  <header>
    <h1>{{ latest.title }}</h1>
  </header>
  {{ latest.content }}
</article>
{% else %}
<p class="empty">The first issue lands tomorrow morning.</p>
{% endif %}

{% if site.posts.size > 1 %}
<section class="archive">
  <h2>Archive</h2>
  <ul>
    {% for post in site.posts offset:1 %}
      <li>
        <a href="{{ post.url | relative_url }}">
          <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%a %d %b %Y" }}</time>
        </a>
      </li>
    {% endfor %}
  </ul>
</section>
{% endif %}
