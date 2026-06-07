---
layout: default
title: "About — Cryptoccino"
description: "What Cryptoccino is, how it's brewed, and who's behind the machine that writes it."
permalink: /about/
---
<section class="about-page" markdown="1">
<header class="archive-head">
  <p class="archive-eyebrow">● About</p>
  <h1>Cryptoccino</h1>
  <p class="archive-sub">Your daily shot of crypto news</p>
</header>

## What this is

A daily Web3 news brief you can read in five minutes over an espresso. Each
morning's issue runs four fixed beats — **Markets** (the majors and the macro),
**Projects & Money** (launches, upgrades, funding, DeFi), the **Security Desk**
(exploits and threat intel), and **On the Hill** (regulators and policy). On a
slow day a beat gets skipped rather than padded.

## How it's brewed

No one writes the copy. A human wrote the machine that does, and the machine
runs on its own every morning:

1. A scheduled job pulls a few dozen RSS feeds and drops anything it has seen
   before (tracked in a small SQLite table).
2. The survivors go through a **single pass** that does everything an editor
   would — picks what matters, clusters the same story told by five outlets into
   one, sorts it into the four beats, and writes the prose.
3. The result is rendered to a static page, committed back to the repository,
   and published by GitHub Pages.

That's the whole newsroom.

## What it isn't

Cryptoccino is a briefing, not advice — nothing here is financial guidance. The
Security Desk is a tripwire, not a teardown: it flags exploits to skim, not deep
technical post-mortems. And it can get things wrong — trust, but verify against
the linked sources.

## Privacy

No cookies, no ad trackers, no consent banner. Visits are counted with
Plausible, which measures traffic without identifying you. Every issue is also
its own [RSS feed]({{ '/feed.xml' | relative_url }}) — read it here or in your
reader.

<div class="colophon" markdown="0">
  <p><strong>Cryptoccino</strong> — your daily shot of crypto news.</p>
  <p>Built with Jekyll, served on GitHub Pages.</p>
  <p>Five roasts: Latte · Cappuccino · Flat White · Espresso · Newsprint.</p>
  <p><a href="https://github.com/JuliusBrain/Cryptoccino">Open source on GitHub</a> · spot an error? <a href="https://github.com/JuliusBrain/Cryptoccino/issues">Open an issue.</a></p>
</div>
</section>
