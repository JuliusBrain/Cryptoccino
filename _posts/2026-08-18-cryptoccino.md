---
layout: issue
title: "Cryptoccino — Tuesday 18 August 2026"
date: 2026-08-18
issue_date: 2026-08-18
description: "Quiet Sunday with loud undercurrents: a long-dormant hardware bug resurfaces, the Treasury starts drawing stablecoin battle lines, and the ETF bid keeps draining."
headline: "A years-old Coldcard firmware bug has now cost users $100 million, and the hardware-wallet trust model is cracking."
lead_slug: a-years-old-coldcard-firmware-bug-has-now-cost-users-100-million-and-the-hardware-wallet-trust-model-is-cracking
card: /assets/cards/2026-08-18.png
beats:
- id: the_tape
  title: Markets
  items:
  - lead_in: Bitcoin ETFs log worst outflow week in six weeks.
    text: Spot bitcoin ETFs shed roughly $390 million across the week, reversing a
      strong start to August and representing the steepest weekly outflow since late
      June. Bitcoin itself has been tracking equity moves, briefly crossing $64,000
      in Asia hours, but the ETF drain keeps any sustained rally look unconvincing.
      Fear & Greed sits at 41 despite a 12-point recovery over the past week, which
      says the bounce in sentiment has not yet translated into fresh capital allocation.
    slug: bitcoin-etfs-log-worst-outflow-week-in-six-weeks
  - lead_in: Bitcoin futures positioning is dangerously crowded.
    text: Open interest relative to available liquidity on major perp venues has reached
      levels where even a modest directional move could trigger a cascade of forced
      unwinds. Options implied vol is also running elevated against realised vol,
      pricing in tail risk even as spot grinds sideways. Traders leaning on leverage
      in either direction should note the exit is narrow.
    slug: bitcoin-futures-positioning-is-dangerously-crowded
  - lead_in: Paul Tudor Jones's fund rotates back into the iShares Bitcoin ETF.
    text: After roughly a year of selling, PTJ's firm raised its IBIT stake 18.9%
      to 688,529 shares worth around $22.9 million in Q2, while simultaneously cutting
      call options exposure sharply. The shift signals a move from leveraged directional
      bets toward plain spot exposure, which reads as a more defensive posture rather
      than a high-conviction long.
    slug: paul-tudor-joness-fund-rotates-back-into-the-ishares-bitcoin-etf
  - lead_in: XRP tests the $1 line it has held since the 2024 US election.
    text: The token slipped to the dollar mark over the weekend, with daily and weekly
      charts now both showing deteriorating momentum. Traders are positioning for
      a rebound, but bearish commentary is the loudest it has been in months, and
      a clean break below $1 would end a nearly two-year streak of support at that
      level.
    slug: xrp-tests-the-1-line-it-has-held-since-the-2024-us-election
- id: projects_money
  title: Projects & Money
  items:
  - lead_in: Bitmine now controls close to 5% of Ethereum's total supply.
    text: Tom Lee's firm added 9,926 ETH last week at a cost of roughly $19 million,
      bringing total holdings to 5.82 million tokens worth around $11 billion. The
      company says it is 96% of the way to its stated 5% target, and buybacks have
      reached 20.8 million shares since July. It is the same treasury-accumulation
      playbook as Strategy but applied to ETH, and the concentration is getting hard
      to ignore.
    slug: bitmine-now-controls-close-to-5-of-ethereums-total-supply
  - lead_in: Compound pivots to institutional lending with $52 million and a new leadership
      team.
    text: The DeFi protocol is repositioning itself away from retail borrowers toward
      institutional clients, committing $52 million to the shift alongside a management
      overhaul. It is a direct acknowledgement that the retail DeFi summer model does
      not generate the sustained revenue that institutions can. Whether Compound can
      compete with purpose-built institutional credit desks is the open question.
    slug: compound-pivots-to-institutional-lending-with-52-million-and-a-new-leadership-team
  - lead_in: Harmony plans a full chain rollback after an exploiter minted 3 trillion
      ONE tokens.
    text: The team considered blacklisting wallets and burning the forged supply but
      concluded a pre-attack rollback was the fairest resolution, which means 109,000
      transactions will be wiped. Ravencoin is separately navigating its own rollback
      dispute from a different exploit, making this an unusually active week for the
      nuclear option in chain governance.
    slug: harmony-plans-a-full-chain-rollback-after-an-exploiter-minted-3-trillion-one-tokens
  - lead_in: Tokenised equities have tripled market share since January, now at $2.8
      billion.
    text: Ondo, Binance and xStocks are leading a segment that has grown its share
      of the broader tokenised asset market to 15%, up from roughly 5% at the start
      of the year. Meanwhile, Robinhood Chain's TVL surged 45% in August, driven almost
      entirely by USDe stablecoin inflows rather than tokenised RWAs, which are actually
      losing ground on that specific chain.
    slug: tokenised-equities-have-tripled-market-share-since-january-now-at-28-billion
- id: security_desk
  title: Security Desk
  items:
  - lead_in: Full Coldcard coverage is in the lead.
    text: See the lead story above for the $100 million Coldcard firmware exploit
      and its implications for hardware wallet security assumptions.
    slug: full-coldcard-coverage-is-in-the-lead
  - lead_in: Bits of Gold data breach exposes 200,000 customers.
    text: Israel's largest crypto broker confirmed a breach affecting the personal
      data of around 200,000 clients. No fund losses are reported, but the scale of
      the PII exposure creates significant phishing and physical attack surface for
      affected users.
    slug: bits-of-gold-data-breach-exposes-200000-customers
  - lead_in: SafePal order-tracking plug-in leaks physical addresses of 40,000 hardware
      wallet buyers.
    text: A vulnerability in a third-party order-tracking tool exposed names, home
      addresses and phone numbers for nearly 40,000 SafePal customers. Hardware wallet
      buyers are a high-value target for wrench attacks, and the combination of name
      plus delivery address is enough to make that risk very concrete.
    slug: safepal-order-tracking-plug-in-leaks-physical-addresses-of-40000-hardware-wallet-buyers
  - lead_in: macOS Screen Sharing auth flaw weaponised for Monero mining.
    text: The Dutch national cyber agency flagged active exploitation of an authentication
      bypass in macOS Screen Sharing that gives attackers root access, which is then
      used to silently deploy XMR miners. Public proof-of-concept code is circulating,
      so patch or disable the feature now.
    slug: macos-screen-sharing-auth-flaw-weaponised-for-monero-mining
- id: on_the_hill
  title: On the Hill
  items:
  - lead_in: US Treasury opens public comment on GENIUS Act stablecoin licensing rules.
    text: The Treasury is now formally soliciting input on regulations that will determine
      who can legally issue or distribute payment stablecoins in the US, with the
      law itself set to take effect in January 2027. The comment window is the first
      real opportunity for the industry to shape the implementation details, including
      which state licences qualify and how foreign issuers are treated. Exchanges
      and platforms distributing stablecoins to US customers face new compliance requirements
      under the proposed framework.
    slug: us-treasury-opens-public-comment-on-genius-act-stablecoin-licensing-rules
  - lead_in: OCC gives conditional approval to Trump family's World Liberty Financial
      for a bank trust charter.
    text: The Office of the Comptroller of the Currency granted the conditional nod
      as ten House Democrats signed onto separate legislation framed explicitly as
      a safeguard against corruption in banking applications. The timing makes the
      approval politically radioactive regardless of its regulatory merits, and the
      Democrats' bill is unlikely to move fast enough to matter.
    slug: occ-gives-conditional-approval-to-trump-familys-world-liberty-financial-for-a-bank-trust-charter
  - lead_in: SIFMA's legal threat has paused the SEC's crypto fundraising rulemaking.
    text: The SEC cited a scheduling conflict when it pulled back a digital-asset
      offering framework, but sources say Wall Street trade body SIFMA threatened
      legal action and the administration is waiting to see whether the Clarity Act
      clears in September before committing to a regulatory path. The delay leaves
      token issuers with no clear federal framework heading into the autumn.
    slug: sifmas-legal-threat-has-paused-the-secs-crypto-fundraising-rulemaking
  - lead_in: Binance handed Russian authorities user data that contributed to the
      arrest of a Ukrainian donor.
    text: Reporting confirms that Binance complied with a Russian law enforcement
      request, sharing account data that was subsequently used to identify and detain
      a Ukrainian who had donated to the war effort. The case is a live illustration
      of the compliance risk that global exchanges face when operating across jurisdictions
      with adversarial governments.
    slug: binance-handed-russian-authorities-user-data-that-contributed-to-the-arrest-of-a-ukrainian-donor
---

<div class="mood-gauge" role="meter" aria-label="Market mood" aria-valuemin="1" aria-valuemax="5" aria-valuenow="1" aria-valuetext="Decaf morning">
  <p class="mood-label">Today's Roast</p>
  <div class="mood-beans"><span class="bean-filled"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span></div>
  <p class="mood-detail"><strong>Decaf morning</strong> · top move 1.2% (BTC)</p>
</div>

<div class="pour-band" markdown="1">

> **The Pour.** Quiet Sunday with loud undercurrents: a long-dormant hardware bug resurfaces, the Treasury starts drawing stablecoin battle lines, and the ETF bid keeps draining.
>
> **Today.** Coldcard bug sat hidden for years, now $100M is gone _Security Desk_ · Bitcoin ETFs post their worst outflow week in six weeks _Markets_ · Treasury opens public comment on GENIUS Act stablecoin rules _On the Hill_.
{: .pour}

<section class="prices">
  <p class="prices-label">Prices</p>
  <ul class="chips">
    <li class="chip"><span class="chip-left"><span class="ticker">BTC</span><span class="price">$64,049</span></span><span class="chip-right"><span class="change up">+1.2%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#4C7A47" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,20.0 4.5,19.2 8.0,19.7 11.4,17.8 14.9,19.6 18.4,21.7 21.9,23.0 25.3,16.5 28.8,17.4 32.3,19.3 35.8,17.3 39.3,12.8 42.7,7.5 46.2,9.0 49.7,5.2 53.2,4.5 56.7,5.8 60.1,3.5 63.6,4.9 67.1,5.5 70.6,1.0 74.0,4.1 77.5,7.3 81.0,9.0"/><circle cx="81.0" cy="9.0" r="1.8" fill="#4C7A47"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">ETH</span><span class="price">$1,890</span></span><span class="chip-right"><span class="change down">−0.5%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,12.9 4.5,12.6 8.0,16.7 11.4,10.0 14.9,16.3 18.4,20.6 21.9,22.3 25.3,8.7 28.8,9.9 32.3,17.2 35.8,13.5 39.3,8.1 42.7,3.0 46.2,8.5 49.7,6.9 53.2,7.4 56.7,8.4 60.1,7.5 63.6,10.9 67.1,10.8 70.6,1.0 74.0,5.4 77.5,14.4 81.0,23.0"/><circle cx="81.0" cy="23.0" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">BNB</span><span class="price">$603</span></span><span class="chip-right"><span class="change down">−0.2%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,10.7 4.5,4.8 8.0,9.2 11.4,5.8 14.9,11.7 18.4,12.8 21.9,17.1 25.3,11.1 28.8,13.1 32.3,17.8 35.8,9.0 39.3,3.4 42.7,1.8 46.2,1.0 49.7,6.5 53.2,7.3 56.7,11.7 60.1,7.6 63.6,13.1 67.1,14.3 70.6,8.3 74.0,11.4 77.5,17.5 81.0,23.0"/><circle cx="81.0" cy="23.0" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">SOL</span><span class="price">$75.37</span></span><span class="chip-right"><span class="change up">+0.0%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,14.6 4.5,14.7 8.0,17.6 11.4,7.1 14.9,9.5 18.4,23.0 21.9,20.1 25.3,8.6 28.8,11.2 32.3,18.9 35.8,13.9 39.3,5.4 42.7,1.0 46.2,3.5 49.7,5.9 53.2,6.7 56.7,9.5 60.1,2.2 63.6,7.9 67.1,9.8 70.6,2.2 74.0,2.1 77.5,13.5 81.0,22.0"/><circle cx="81.0" cy="22.0" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">XRP</span><span class="price">$0.9893</span></span><span class="chip-right"><span class="change down">−1.1%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,5.0 4.5,5.2 8.0,7.3 11.4,1.0 14.9,5.2 18.4,11.9 21.9,13.8 25.3,6.1 28.8,7.8 32.3,12.6 35.8,10.2 39.3,3.9 42.7,1.5 46.2,5.5 49.7,7.9 53.2,7.8 56.7,8.3 60.1,4.2 63.6,8.4 67.1,8.7 70.6,4.5 74.0,5.3 77.5,14.8 81.0,23.0"/><circle cx="81.0" cy="23.0" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">DOGE</span><span class="price">$0.0697</span></span><span class="chip-right"><span class="change down">−0.4%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,7.9 4.5,7.7 8.0,9.3 11.4,2.0 14.9,5.4 18.4,12.4 21.9,7.0 25.3,2.8 28.8,9.2 32.3,13.8 35.8,9.4 39.3,4.7 42.7,1.0 46.2,4.5 49.7,4.3 53.2,4.9 56.7,7.1 60.1,4.7 63.6,7.1 67.1,8.1 70.6,2.8 74.0,4.5 77.5,13.9 81.0,23.0"/><circle cx="81.0" cy="23.0" r="1.8" fill="#B14A33"/></svg></span></li>
  </ul>
</section>

</div>

<section class="lead" markdown="1">

**SECURITY DESK**
{: .kicker}

## A years-old Coldcard firmware bug has now cost users $100 million, and the hardware-wallet trust model is cracking.
{: #a-years-old-coldcard-firmware-bug-has-now-cost-users-100-million-and-the-hardware-wallet-trust-model-is-cracking}

[`coindesk`](https://www.coindesk.com/tech/2026/08/17/how-a-bug-in-coldcard-s-code-went-unnoticed-for-years-leading-to-usd100-million-in-hacked-funds) [`coindesk`](https://www.coindesk.com/opinion/2026/08/17/the-coldcard-hack-proves-reputation-is-not-a-security-model)
{: .sources}

<div class="fng-chip" aria-label="Crypto Fear &amp; Greed Index" title="Crypto Fear &amp; Greed Index. Scale 0 (extreme fear) to 100 (extreme greed)."><span class="fng-label">Fear &amp; Greed</span><span class="fng-value">41<span class="fng-scale">/100</span></span><span class="fng-class">Fear</span> <span class="fng-delta up">+12 / 7d</span></div>

**What happened.** A latent code defect in Coldcard's firmware, present for several years without detection, has been exploited to drain roughly $100 million from affected wallets. The flaw was deep enough in the signing logic that standard user behaviour offered no protection, and neither public audits nor Coldcard's reputation as a security-first device flagged it.

**Why it matters.** Hardware wallets sit at the top of most self-custody security stacks precisely because they are assumed to be the last line of defence. A confirmed, long-lived bug of this scale forces a reassessment of every assumption built on top of that trust, from custody policy at funds to individual high-net-worth holders who moved coins specifically to avoid exchange risk.

**The catch.** Coldcard has not yet published a full post-mortem or confirmed which firmware versions are affected, leaving current users with no clean remediation path beyond moving funds now and waiting. The broader lesson, underscored by the accompanying op-ed, is that brand reputation and community goodwill do not constitute a security model, and no hardware device should be treated as audited simply because it is popular.

</section>

<img class="section-card" id="the_tape" src="{{ "/assets/cards/2026-08-18-the_tape.png" | relative_url }}" alt="Markets" width="1200" height="300" loading="lazy" decoding="async">

> **Bitcoin ETFs log worst outflow week in six weeks.** Spot bitcoin ETFs shed roughly $390 million across the week, reversing a strong start to August and representing the steepest weekly outflow since late June. Bitcoin itself has been tracking equity moves, briefly crossing $64,000 in Asia hours, but the ETF drain keeps any sustained rally look unconvincing. Fear &amp; Greed sits at 41 despite a 12-point recovery over the past week, which says the bounce in sentiment has not yet translated into fresh capital allocation. [`bloomberg_crypto`](https://www.bloomberg.com/news/articles/2026-08-17/bitcoin-etfs-see-largest-outflow-in-six-weeks-as-token-stagnates) [`coindesk`](https://www.coindesk.com/markets/2026/08/17/bitcoin-tracks-equity-bounce-but-usd390-million-etf-outflow-week-keeps-bulls-on-back-foot)
{: #bitcoin-etfs-log-worst-outflow-week-in-six-weeks}

> **Bitcoin futures positioning is dangerously crowded.** Open interest relative to available liquidity on major perp venues has reached levels where even a modest directional move could trigger a cascade of forced unwinds. Options implied vol is also running elevated against realised vol, pricing in tail risk even as spot grinds sideways. Traders leaning on leverage in either direction should note the exit is narrow. [`coindesk`](https://www.coindesk.com/markets/2026/08/17/the-bitcoin-futures-market-has-a-crowded-club-tiny-exit-problem-and-it-could-cause-pain) [`coindesk`](https://www.coindesk.com/markets/2026/08/17/bitcoin-options-remain-expensive-despite-summer-calm-here-s-why-it-matters)
{: #bitcoin-futures-positioning-is-dangerously-crowded}

> **Paul Tudor Jones's fund rotates back into the iShares Bitcoin ETF.** After roughly a year of selling, PTJ's firm raised its IBIT stake 18.9% to 688,529 shares worth around $22.9 million in Q2, while simultaneously cutting call options exposure sharply. The shift signals a move from leveraged directional bets toward plain spot exposure, which reads as a more defensive posture rather than a high-conviction long. [`decrypt`](https://decrypt.co/375745/paul-tudor-jones-buys-blackrock-bitcoin-etf)
{: #paul-tudor-joness-fund-rotates-back-into-the-ishares-bitcoin-etf}

> **XRP tests the $1 line it has held since the 2024 US election.** The token slipped to the dollar mark over the weekend, with daily and weekly charts now both showing deteriorating momentum. Traders are positioning for a rebound, but bearish commentary is the loudest it has been in months, and a clean break below $1 would end a nearly two-year streak of support at that level. [`coindesk`](https://www.coindesk.com/markets/2026/08/17/xrp-traders-bet-on-a-rebound-as-price-slips-to-usd1-and-bearish-chatter-surges) [`decrypt`](https://decrypt.co/375794/xrp-price-two-year-streak-charts-flash-warning)
{: #xrp-tests-the-1-line-it-has-held-since-the-2024-us-election}

<img class="section-card" id="projects_money" src="{{ "/assets/cards/2026-08-18-projects_money.png" | relative_url }}" alt="Projects &amp; Money" width="1200" height="300" loading="lazy" decoding="async">

> **Bitmine now controls close to 5% of Ethereum's total supply.** Tom Lee's firm added 9,926 ETH last week at a cost of roughly $19 million, bringing total holdings to 5.82 million tokens worth around $11 billion. The company says it is 96% of the way to its stated 5% target, and buybacks have reached 20.8 million shares since July. It is the same treasury-accumulation playbook as Strategy but applied to ETH, and the concentration is getting hard to ignore. [`theblock`](https://www.theblock.co/news/business/2026-08-17-bitmine-adds-9926-eth-taking-total-holdings-to-roughly-11-billion-411968) [`coindesk`](https://www.coindesk.com/markets/2026/08/17/tom-lee-s-bitmine-now-owns-4-8-of-ethereum-supply-after-latest-eth-purchase) [`decrypt`](https://decrypt.co/375768/tom-lee-bitcoin-buys-19-million-ethereum)
{: #bitmine-now-controls-close-to-5-of-ethereums-total-supply}

> **Compound pivots to institutional lending with $52 million and a new leadership team.** The DeFi protocol is repositioning itself away from retail borrowers toward institutional clients, committing $52 million to the shift alongside a management overhaul. It is a direct acknowledgement that the retail DeFi summer model does not generate the sustained revenue that institutions can. Whether Compound can compete with purpose-built institutional credit desks is the open question. [`coindesk`](https://www.coindesk.com/business/2026/08/17/compound-bets-usd52-million-new-leadership-team-in-switch-to-institutional-focus)
{: #compound-pivots-to-institutional-lending-with-52-million-and-a-new-leadership-team}

> **Harmony plans a full chain rollback after an exploiter minted 3 trillion ONE tokens.** The team considered blacklisting wallets and burning the forged supply but concluded a pre-attack rollback was the fairest resolution, which means 109,000 transactions will be wiped. Ravencoin is separately navigating its own rollback dispute from a different exploit, making this an unusually active week for the nuclear option in chain governance. [`theblock`](https://www.theblock.co/news/ecosystems/2026-08-17-harmony-plans-pre-attack-rollback-after-exploiter-forged-3-trillion-one-tokens-411976) [`cointelegraph_defi`](https://cointelegraph.com/news/harmony-plans-rollback-transactions-one-exploit)
{: #harmony-plans-a-full-chain-rollback-after-an-exploiter-minted-3-trillion-one-tokens}

> **Tokenised equities have tripled market share since January, now at $2.8 billion.** Ondo, Binance and xStocks are leading a segment that has grown its share of the broader tokenised asset market to 15%, up from roughly 5% at the start of the year. Meanwhile, Robinhood Chain's TVL surged 45% in August, driven almost entirely by USDe stablecoin inflows rather than tokenised RWAs, which are actually losing ground on that specific chain. [`theblock`](https://www.theblock.co/news/defi/2026-08-17-tokenized-equities-triple-market-share-ondo-binance-xstocks-dominate-411996) [`theblock`](https://www.theblock.co/news/ecosystems/2026-08-17-robinhood-chain-tvl-surges-45-august-tokenized-rwas-lose-ground-411998)
{: #tokenised-equities-have-tripled-market-share-since-january-now-at-28-billion}

<img class="section-card" id="security_desk" src="{{ "/assets/cards/2026-08-18-security_desk.png" | relative_url }}" alt="Security Desk" width="1200" height="300" loading="lazy" decoding="async">

> **Full Coldcard coverage is in the lead.** See the lead story above for the $100 million Coldcard firmware exploit and its implications for hardware wallet security assumptions. [`coindesk`](https://www.coindesk.com/tech/2026/08/17/how-a-bug-in-coldcard-s-code-went-unnoticed-for-years-leading-to-usd100-million-in-hacked-funds)
{: #full-coldcard-coverage-is-in-the-lead}

> **Bits of Gold data breach exposes 200,000 customers.** Israel's largest crypto broker confirmed a breach affecting the personal data of around 200,000 clients. No fund losses are reported, but the scale of the PII exposure creates significant phishing and physical attack surface for affected users. [`coindesk`](https://www.coindesk.com/tech/2026/08/17/israel-s-largest-crypto-broker-bits-of-gold-hit-by-data-breach-affecting-200-000-customers)
{: #bits-of-gold-data-breach-exposes-200000-customers}

> **SafePal order-tracking plug-in leaks physical addresses of 40,000 hardware wallet buyers.** A vulnerability in a third-party order-tracking tool exposed names, home addresses and phone numbers for nearly 40,000 SafePal customers. Hardware wallet buyers are a high-value target for wrench attacks, and the combination of name plus delivery address is enough to make that risk very concrete. [`decrypt`](https://decrypt.co/375743/safepal-bitcoin-wallet-data-breach)
{: #safepal-order-tracking-plug-in-leaks-physical-addresses-of-40000-hardware-wallet-buyers}

> **macOS Screen Sharing auth flaw weaponised for Monero mining.** The Dutch national cyber agency flagged active exploitation of an authentication bypass in macOS Screen Sharing that gives attackers root access, which is then used to silently deploy XMR miners. Public proof-of-concept code is circulating, so patch or disable the feature now. [`decrypt`](https://decrypt.co/375749/hackers-macos-screen-sharing-secretly-mine-monero)
{: #macos-screen-sharing-auth-flaw-weaponised-for-monero-mining}

<img class="section-card" id="on_the_hill" src="{{ "/assets/cards/2026-08-18-on_the_hill.png" | relative_url }}" alt="On the Hill" width="1200" height="300" loading="lazy" decoding="async">

> **US Treasury opens public comment on GENIUS Act stablecoin licensing rules.** The Treasury is now formally soliciting input on regulations that will determine who can legally issue or distribute payment stablecoins in the US, with the law itself set to take effect in January 2027. The comment window is the first real opportunity for the industry to shape the implementation details, including which state licences qualify and how foreign issuers are treated. Exchanges and platforms distributing stablecoins to US customers face new compliance requirements under the proposed framework. [`coindesk`](https://www.coindesk.com/policy/2026/08/17/u-s-treasury-department-proposes-genius-act-stablecoin-rule) [`theblock`](https://www.theblock.co/news/regulation/2026-08-17-us-treasury-seeks-public-comment-genius-act-stablecoin-rules-411987) [`cointelegraph_regulation`](https://cointelegraph.com/news/us-treasury-public-comment-rules-genius-act) [`decrypt`](https://decrypt.co/375817/treasury-rules-sell-stablecoins-us)
{: #us-treasury-opens-public-comment-on-genius-act-stablecoin-licensing-rules}

> **OCC gives conditional approval to Trump family's World Liberty Financial for a bank trust charter.** The Office of the Comptroller of the Currency granted the conditional nod as ten House Democrats signed onto separate legislation framed explicitly as a safeguard against corruption in banking applications. The timing makes the approval politically radioactive regardless of its regulatory merits, and the Democrats' bill is unlikely to move fast enough to matter. [`cointelegraph_regulation`](https://cointelegraph.com/news/occ-donald-trump-world-liberty-financial-trust-charter)
{: #occ-gives-conditional-approval-to-trump-familys-world-liberty-financial-for-a-bank-trust-charter}

> **SIFMA's legal threat has paused the SEC's crypto fundraising rulemaking.** The SEC cited a scheduling conflict when it pulled back a digital-asset offering framework, but sources say Wall Street trade body SIFMA threatened legal action and the administration is waiting to see whether the Clarity Act clears in September before committing to a regulatory path. The delay leaves token issuers with no clear federal framework heading into the autumn. [`decrypt`](https://decrypt.co/375779/wall-street-pushback-halts-sec-crypto-fundraising-framework)
{: #sifmas-legal-threat-has-paused-the-secs-crypto-fundraising-rulemaking}

> **Binance handed Russian authorities user data that contributed to the arrest of a Ukrainian donor.** Reporting confirms that Binance complied with a Russian law enforcement request, sharing account data that was subsequently used to identify and detain a Ukrainian who had donated to the war effort. The case is a live illustration of the compliance risk that global exchanges face when operating across jurisdictions with adversarial governments. [`coindesk`](https://www.coindesk.com/policy/2026/08/17/binance-handed-user-data-to-russia-that-led-to-a-ukrainian-donor-s-arrest)
{: #binance-handed-russian-authorities-user-data-that-contributed-to-the-arrest-of-a-ukrainian-donor}

## What else is grinding?
{: .brewing-label}

- Austria's FMA fined Bitpanda €70,000 for white paper and marketing disclosure failures, marking the first published MiCA enforcement action in the country. [`theblock`](https://www.theblock.co/news/regulation/2026-08-17-austria-mica-penalty-bitpanda-411960) [`coindesk`](https://www.coindesk.com/business/2026/08/17/bitpanda-fined-eur70-000-in-austria-s-first-published-mica-enforcement-case)
- Strategy raised $334 million by selling MSTR shares last week but made no bitcoin purchases, letting its dollar reserve climb to $4.8 billion while Saylor said buybacks are a possibility but not the priority. [`theblock`](https://www.theblock.co/news/business/2026-08-17-michael-saylor-strategy-btc-411942) [`decrypt`](https://decrypt.co/375762/strategy-leaves-bitcoin-untouched-raises-334m-selling-mstr-stock)
- Ethereum's next upgrade is carrying 66 EIPs, with a headline privacy proposal that would allow shielded pools to pay their own gas fees without an intermediary. [`coindesk`](https://www.coindesk.com/tech/2026/08/17/ethereum-s-next-big-upgrade-has-66-proposals-including-a-major-privacy-fix) [`decrypt`](https://decrypt.co/375787/ethereum-developers-privacy-hegota-upgrade)
- Binance is reportedly planning a fresh FCA licence application to re-enter the UK retail market after being barred from regulated activities there since 2021. [`cointelegraph_regulation`](https://cointelegraph.com/news/binance-uk-launch-plans-fca-license)
- Pirated downloads of the film 'The Odyssey' are already bundling Lumma Stealer, malware that exfiltrates crypto wallet credentials and browser sessions from infected machines. [`decrypt`](https://decrypt.co/375747/pirated-copies-odyssey-hiding-crypto-stealing-malware)
- BitMart's founder rejected calls for an independent audit as users publicly reported frozen withdrawals and employees described unpaid wages. [`coindesk`](https://www.coindesk.com/business/2026/08/17/bitmart-founder-dismisses-calls-for-audit-as-users-report-blocked-funds-unpaid-employees)

---

> **Last sip.** Coldcard's full firmware post-mortem still hasn't landed, and until it does, nobody knows how many devices are still holding live exposure.
{: .last-sip}
