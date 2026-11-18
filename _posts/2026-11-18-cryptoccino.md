---
layout: issue
title: "Cryptoccino — Wednesday 18 November 2026"
date: 2026-11-18
issue_date: 2026-11-18
description: "Markets flush, code weaponised, and a federal judge hands MEV a legal landmark nobody quite expected."
headline: "Optimizely supply-chain compromise plants wallet-draining malware on 178 major sites, Ledger and HSBC among them."
lead_slug: optimizely-supply-chain-compromise-plants-wallet-draining-malware-on-178-major-sites-ledger-and-hsbc-among-them
card: /assets/cards/2026-11-18.png
beats:
- id: the_tape
  title: Markets
  items:
  - lead_in: Bitcoin breaks its 200-week moving average by 12%, but the pattern is
      historically bullish.
    text: BTC has now closed below the 200-week MA, a breach that has occurred only
      a handful of times in its history. Glassnode data show realised losses at levels
      seen near the 2018, 2020, 2022 and early 2023 lows — capitulation readings that
      have preceded recoveries each time. With the Fear & Greed Index at 11 (Extreme
      Fear) and down 18 points over the past week, the sentiment setup mirrors those
      prior bottoms even if the macro backdrop is less forgiving.
    slug: bitcoin-breaks-its-200-week-moving-average-by-12-but-the-pattern-is-historically-bullish
  - lead_in: Wintermute warns BTC could revisit the $50,000s as Fed rate-hike bets
      build.
    text: The desk cites tightening financial conditions and persistent ETF outflows
      as the structural headwind, noting that the liquidity backdrop that drove last
      year's rally is no longer present. Bitcoin spent much of yesterday range-bound
      near $64,000 even after the ETF outflow streak briefly ended, suggesting buyers
      are not yet stepping in with conviction.
    slug: wintermute-warns-btc-could-revisit-the-50000s-as-fed-rate-hike-bets-build
  - lead_in: XRP whales shifted $270 million during the selloff — none of it went
      to exchanges.
    text: On-chain data show the large transfers routed to private wallets rather
      than exchange deposit addresses, which analysts read as accumulation rather
      than distribution. XRP has fallen below $1 during the broader drawdown, though
      the whale behaviour suggests at least some large holders are treating the dip
      as a holding opportunity.
    slug: xrp-whales-shifted-270-million-during-the-selloff-none-of-it-went-to-exchanges
  - lead_in: Nvidia beat earnings and lifted guidance, but leadership uncertainty
      is unresolved.
    text: The chipmaker doubled quarterly revenue and authorised a further $150 billion
      in buybacks in its first report since Jensen Huang's exit, sending shares up
      roughly 2.5% after hours. The board has formally rejected a Huang comeback and
      hired a search firm, though Huang himself has said he would return if asked.
      The result provides a data point that operations remain intact, but the leadership
      overhang and China export scrutiny continue to weigh.
    slug: nvidia-beat-earnings-and-lifted-guidance-but-leadership-uncertainty-is-unresolved
- id: projects_money
  title: Projects & Money
  items:
  - lead_in: Solana Foundation takes a majority stake in CoinGecko as the data aggregator
      eyes trading.
    text: The deal hands the Foundation a controlling interest in one of crypto's
      most-trafficked data properties and gives CoinGecko resources to build out market-intelligence
      and trading products. It deepens Solana's institutional footprint at a moment
      when the network is actively pitching itself to TradFi, and puts a neutral-brand
      data platform inside an ecosystem player's portfolio.
    slug: solana-foundation-takes-a-majority-stake-in-coingecko-as-the-data-aggregator-eyes-trading
  - lead_in: World Bank, Circle and Citi begin piloting USDC rails for development
      fund disbursements.
    text: The initiative will test an intermediated, interoperable stablecoin model
      for getting money to recipients faster and more cheaply than traditional correspondent-banking
      routes. If it clears the pilot stage, it represents a meaningful institutional
      validation of USDC as settlement infrastructure rather than just a trading vehicle.
    slug: world-bank-circle-and-citi-begin-piloting-usdc-rails-for-development-fund-disbursements
  - lead_in: Coinbase extends onchain crypto loans to New York via Morpho, with BTC,
      ETH and SOL as collateral.
    text: New York has been a persistent holdout for many crypto product launches
      given its BitLicense regime, so the expansion is a signal that the regulatory
      path is now navigable. Borrowers put up crypto and receive USDC without a credit
      check; the protocol handles liquidation mechanics on-chain.
    slug: coinbase-extends-onchain-crypto-loans-to-new-york-via-morpho-with-btc-eth-and-sol-as-collateral
  - lead_in: Ethereum's Glamsterdam upgrade could break up to 15,000 deployed contracts.
    text: 'Core developers flagged on a recent call that two proposed scaling changes,
      which together would deliver a 3.3x capacity boost, violate assumptions baked
      into a large number of live contracts. The tension is a classic upgrade trilemma:
      meaningful throughput gains versus meaningful breakage risk for existing apps.
      No resolution date has been set.'
    slug: ethereums-glamsterdam-upgrade-could-break-up-to-15000-deployed-contracts
- id: security_desk
  title: Security Desk
  items:
  - lead_in: Optimizely supply-chain attack hits 178 sites with wallet-draining and
      card-skimming malware.
    text: 'Full write-up in the lead. TL;DR: audit your third-party script allowlists
      and enforce CSP.'
    slug: optimizely-supply-chain-attack-hits-178-sites-with-wallet-draining-and-card-skimming-malware
  - lead_in: Binance hack wallets move $137 million in ETH after a two-week dormancy.
    text: A wallet tied to October's record Binance exploit shifted $63 million in
      ether, with analysts then flagging a broader wave totalling roughly $137 million
      across related addresses. Some funds were also swapped into Bitcoin. U.S. recovery
      efforts are ongoing.
    slug: binance-hack-wallets-move-137-million-in-eth-after-a-two-week-dormancy
  - lead_in: Lighter exchange reopens after a single trader's leaked API key drained
      roughly $5 million in USDC.
    text: The incident was not a protocol exploit but an API-key compromise that routed
      funds through trade and internal-transfer paths that lacked adequate withdrawal
      controls. Lighter returned the full $5 million to the affected trader and has
      since reopened deposits and withdrawals.
    slug: lighter-exchange-reopens-after-a-single-traders-leaked-api-key-drained-roughly-5-million-in-usdc
  - lead_in: 'SEAL weekly triage: 85 incidents logged in the past seven days.'
    text: Security Alliance's radar report covers losses by threat category and publishes
      IOCs for the week ending 17 November. No single dominant attack vector is called
      out, suggesting continued broad-based opportunistic activity.
    slug: seal-weekly-triage-85-incidents-logged-in-the-past-seven-days
- id: on_the_hill
  title: On the Hill
  items:
  - lead_in: Federal judge acquits MIT brothers in the $25 million Ethereum MEV case
      — ruling Ethereum has no terms of use.
    text: Judge Jessica Clarke found prosecutors could not prove the material misrepresentation
      required for wire fraud, reasoning that because the Ethereum protocol has no
      terms of use, exploiting MEV ordering is not a false promise to any counterparty.
      The ruling comes a year after a jury deadlocked and does not adjudicate whether
      the conduct was ethical, only that it was not criminal under the wire fraud
      statute. It is the most consequential judicial statement on MEV legality to
      date.
    slug: federal-judge-acquits-mit-brothers-in-the-25-million-ethereum-mev-case-ruling-ethereum-has-no-terms-of-use
  - lead_in: CFTC formally greenlights perpetuals in the US, with Backpack as the
      first approved venue.
    text: Chairman Mike Selig framed the approval as a milestone and signalled more
      venues would follow. The move ends years of regulatory ambiguity around onshore
      perps and sets a compliance template for other platforms seeking CFTC authorisation.
    slug: cftc-formally-greenlights-perpetuals-in-the-us-with-backpack-as-the-first-approved-venue
  - lead_in: Trump's CFTC nominees face Senate questions over prediction markets;
      Kalshi ordered to pause Trump-mention contracts.
    text: Both nominees voiced scepticism about the public benefit of event contracts,
      with one saying the CFTC must weigh that question carefully. Separately, Kalshi
      has complied with a CFTC order to halt its Trump-mention markets while the regulator
      reviews manipulation risks, with a December 11 deadline to defend the contracts.
    slug: trumps-cftc-nominees-face-senate-questions-over-prediction-markets-kalshi-ordered-to-pause-trump-mention-contracts
  - lead_in: Former Robinhood engineer pleads guilty to insider trading via Hyperliquid
      perps ahead of listing announcements.
    text: Huaisong Xiang admitted using confidential knowledge of upcoming Robinhood
      token listings to trade perpetual futures on Hyperliquid, netting $125,523.
      He faces up to 20 years for wire fraud. The case establishes that classical
      insider-trading logic extends cleanly onto decentralised derivatives venues.
    slug: former-robinhood-engineer-pleads-guilty-to-insider-trading-via-hyperliquid-perps-ahead-of-listing-announcements
---

<div class="mood-gauge" role="meter" aria-label="Market mood" aria-valuemin="1" aria-valuemax="5" aria-valuenow="2" aria-valuetext="Single shot">
  <p class="mood-label">Today's Roast</p>
  <div class="mood-beans"><span class="bean-filled"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-filled"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span><span class="bean-empty"><svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true"><ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/><path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/></svg></span></div>
  <p class="mood-detail"><strong>Single shot</strong> · top move 3.2% (SOL)</p>
</div>

<div class="pour-band" markdown="1">

> **The Pour.** Markets flush, code weaponised, and a federal judge hands MEV a legal landmark nobody quite expected.
>
> **Today.** Bitcoin breaks its 200-week average with the Fear &amp; Greed index at Extreme Fear — history says this is where bottoms form _Markets_ · Optimizely supply-chain hack served crypto-stealing malware across 178 sites including Ledger and HSBC _Security Desk_ · Federal judge acquits MIT brothers in $25M Ethereum MEV case, ruling the protocol has no terms of use _On the Hill_.
{: .pour}

<section class="prices">
  <p class="prices-label">Prices</p>
  <ul class="chips">
    <li class="chip"><span class="chip-left"><span class="ticker">BTC</span><span class="price">$64,647</span></span><span class="chip-right"><span class="change down">−0.5%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,2.2 4.5,5.7 8.0,10.2 11.4,7.1 14.9,13.6 18.4,13.1 21.9,17.4 25.3,3.2 28.8,2.1 32.3,1.0 35.8,3.1 39.3,16.9 42.7,22.9 46.2,21.8 49.7,22.8 53.2,23.0 56.7,19.5 60.1,13.6 63.6,7.5 67.1,4.0 70.6,6.6 74.0,14.0 77.5,13.9 81.0,11.8"/><circle cx="81.0" cy="11.8" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">ETH</span><span class="price">$1,812</span></span><span class="chip-right"><span class="change down">−1.5%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,1.0 4.5,1.2 8.0,4.6 11.4,2.1 14.9,6.9 18.4,10.1 21.9,19.3 25.3,6.1 28.8,5.7 32.3,3.4 35.8,9.1 39.3,20.8 42.7,23.0 46.2,19.6 49.7,18.8 53.2,18.2 56.7,15.0 60.1,12.6 63.6,9.1 67.1,5.2 70.6,7.0 74.0,13.5 77.5,13.3 81.0,12.8"/><circle cx="81.0" cy="12.8" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">BNB</span><span class="price">$592</span></span><span class="chip-right"><span class="change down">−0.3%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#B14A33" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,4.8 4.5,7.2 8.0,9.1 11.4,7.6 14.9,10.7 18.4,12.5 21.9,18.7 25.3,5.9 28.8,6.5 32.3,8.5 35.8,10.2 39.3,18.2 42.7,23.0 46.2,19.2 49.7,18.4 53.2,17.5 56.7,14.8 60.1,11.9 63.6,8.2 67.1,1.0 70.6,4.0 74.0,10.9 77.5,10.6 81.0,10.7"/><circle cx="81.0" cy="10.7" r="1.8" fill="#B14A33"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">SOL</span><span class="price">$75.28</span></span><span class="chip-right"><span class="change up">+3.2%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#4C7A47" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,16.1 4.5,18.6 8.0,18.9 11.4,16.7 14.9,20.3 18.4,18.3 21.9,22.6 25.3,13.0 28.8,11.7 32.3,10.9 35.8,11.0 39.3,20.1 42.7,23.0 46.2,20.8 49.7,20.3 53.2,17.6 56.7,16.0 60.1,12.9 63.6,8.8 67.1,1.0 70.6,2.6 74.0,7.6 77.5,5.6 81.0,3.7"/><circle cx="81.0" cy="3.7" r="1.8" fill="#4C7A47"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">XRP</span><span class="price">$0.9851</span></span><span class="chip-right"><span class="change up">+2.0%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#4C7A47" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,14.7 4.5,17.5 8.0,21.0 11.4,18.0 14.9,22.0 18.4,20.1 21.9,23.0 25.3,11.2 28.8,10.6 32.3,6.3 35.8,10.0 39.3,20.0 42.7,22.1 46.2,21.0 49.7,21.8 53.2,15.7 56.7,13.5 60.1,12.0 63.6,8.9 67.1,1.0 70.6,5.9 74.0,9.0 77.5,8.6 81.0,6.1"/><circle cx="81.0" cy="6.1" r="1.8" fill="#4C7A47"/></svg></span></li>
    <li class="chip"><span class="chip-left"><span class="ticker">DOGE</span><span class="price">$0.0595</span></span><span class="chip-right"><span class="change up">+0.4%</span><svg class="spark" viewBox="0 0 82 24" width="82" height="24" preserveAspectRatio="none"><polyline fill="none" stroke="#4C7A47" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="1.0,10.5 4.5,12.8 8.0,15.3 11.4,12.5 14.9,16.4 18.4,16.7 21.9,21.6 25.3,9.7 28.8,8.8 32.3,8.0 35.8,9.7 39.3,21.2 42.7,23.0 46.2,18.9 49.7,18.6 53.2,13.6 56.7,9.4 60.1,10.3 63.6,6.2 67.1,1.0 70.6,5.8 74.0,11.6 77.5,12.0 81.0,10.1"/><circle cx="81.0" cy="10.1" r="1.8" fill="#4C7A47"/></svg></span></li>
  </ul>
</section>

</div>

<section class="lead" markdown="1">

**SECURITY**
{: .kicker}

## Optimizely supply-chain compromise plants wallet-draining malware on 178 major sites, Ledger and HSBC among them.
{: #optimizely-supply-chain-compromise-plants-wallet-draining-malware-on-178-major-sites-ledger-and-hsbc-among-them}

[`krebsonsecurity`](https://krebsonsecurity.com/2026/11/attackers-used-optimizely-to-a-b-test-malware-on-top-websites/) [`decrypt`](https://decrypt.co/383414/optimizely-hack-hijacked-ledger-bbc-and-176-other-sites-to-swap-crypto-wallet-addresses/) [`coindesk`](https://www.coindesk.com/tech/2026/11/17/hackers-planted-crypto-stealing-code-on-178-organizations-sites-including-hsbc-bbc-and-ledger)
{: .sources}

<div class="fng-chip" aria-label="Crypto Fear &amp; Greed Index" title="Crypto Fear &amp; Greed Index. Scale 0 (extreme fear) to 100 (extreme greed)."><span class="fng-label">Fear &amp; Greed</span><span class="fng-value">11<span class="fng-scale">/100</span></span><span class="fng-class">Extreme Fear</span> <span class="fng-delta down">−18 / 7d</span></div>

**What happened.** Attackers exploited Optimizely, the A/B testing and personalisation platform, to inject malicious scripts into at least 178 high-traffic websites over a 24-hour window. The code silently swapped visitors' crypto wallet addresses with the attacker's own and also skimmed payment card data. Affected properties included Ledger, HSBC, the BBC, CNN, Equifax and Zoom.

**Why it matters.** This is a textbook third-party supply-chain attack: none of the 178 sites were directly compromised, yet every one of their users was exposed. The blast radius reflects how few sites enforce strict Content Security Policies that would block unauthorised script sources. For crypto operators specifically, Ledger's inclusion is pointed — users trusting a hardware wallet vendor's own site are exactly the population most likely to have funds worth taking.

**The catch.** Krebs notes the attack was exacerbated by the near-universal practice of loading third-party optimisation tools without integrity checks. Patching Optimizely closes this vector, but the underlying CSP hygiene problem remains industry-wide. Any team running similar testing or analytics scripts should audit their allowed script sources today.

</section>

<img class="section-card" id="the_tape" src="{{ "/assets/cards/2026-11-18-the_tape.png" | relative_url }}" alt="Markets" width="1200" height="300" loading="lazy" decoding="async">

> **Bitcoin breaks its 200-week moving average by 12%, but the pattern is historically bullish.** BTC has now closed below the 200-week MA, a breach that has occurred only a handful of times in its history. Glassnode data show realised losses at levels seen near the 2018, 2020, 2022 and early 2023 lows — capitulation readings that have preceded recoveries each time. With the Fear &amp; Greed Index at 11 (Extreme Fear) and down 18 points over the past week, the sentiment setup mirrors those prior bottoms even if the macro backdrop is less forgiving. [`coindesk`](https://www.coindesk.com/markets/2026/11/18/bitcoin-s-rare-12-crash-through-its-200-week-average-has-a-bullish-track-record) [`cryptobriefing`](https://cryptobriefing.com/bitcoin-falls-below-200-week-average/) [`decrypt`](https://decrypt.co/383466/bitcoin-investors-capitulating-historical-bottom-signal)
{: #bitcoin-breaks-its-200-week-moving-average-by-12-but-the-pattern-is-historically-bullish}

> **Wintermute warns BTC could revisit the $50,000s as Fed rate-hike bets build.** The desk cites tightening financial conditions and persistent ETF outflows as the structural headwind, noting that the liquidity backdrop that drove last year's rally is no longer present. Bitcoin spent much of yesterday range-bound near $64,000 even after the ETF outflow streak briefly ended, suggesting buyers are not yet stepping in with conviction. [`coindesk`](https://www.coindesk.com/markets/2026/11/17/bitcoin-could-slide-into-the-usd50-000s-as-fed-rate-hike-bets-build-wintermute-says) [`cryptobriefing`](https://cryptobriefing.com/bitcoin-below-65000-crypto-liquidity-drains/)
{: #wintermute-warns-btc-could-revisit-the-50000s-as-fed-rate-hike-bets-build}

> **XRP whales shifted $270 million during the selloff — none of it went to exchanges.** On-chain data show the large transfers routed to private wallets rather than exchange deposit addresses, which analysts read as accumulation rather than distribution. XRP has fallen below $1 during the broader drawdown, though the whale behaviour suggests at least some large holders are treating the dip as a holding opportunity. [`coindesk`](https://www.coindesk.com/markets/2026/11/18/xrp-whales-moved-usd270-million-during-the-selloff-the-coins-didn-t-go-to-exchanges) [`cryptobriefing`](https://cryptobriefing.com/xrp-whales-move-270m-off-exchanges-amid-price-drop-below-1/)
{: #xrp-whales-shifted-270-million-during-the-selloff-none-of-it-went-to-exchanges}

> **Nvidia beat earnings and lifted guidance, but leadership uncertainty is unresolved.** The chipmaker doubled quarterly revenue and authorised a further $150 billion in buybacks in its first report since Jensen Huang's exit, sending shares up roughly 2.5% after hours. The board has formally rejected a Huang comeback and hired a search firm, though Huang himself has said he would return if asked. The result provides a data point that operations remain intact, but the leadership overhang and China export scrutiny continue to weigh. [`coindesk`](https://www.coindesk.com/markets/2026/11/17/nvidia-tops-estimates-issues-strong-guidance-adds-usd150-billion-to-buyback-authorization) [`decrypt`](https://decrypt.co/383505/nvidia-shares-rise-earnings-beat-first-report-jensen-huang-exit) [`cryptobriefing`](https://cryptobriefing.com/nvidia-earnings-q3-fiscal-2027-2026-11/)
{: #nvidia-beat-earnings-and-lifted-guidance-but-leadership-uncertainty-is-unresolved}

<img class="section-card" id="projects_money" src="{{ "/assets/cards/2026-11-18-projects_money.png" | relative_url }}" alt="Projects &amp; Money" width="1200" height="300" loading="lazy" decoding="async">

> **Solana Foundation takes a majority stake in CoinGecko as the data aggregator eyes trading.** The deal hands the Foundation a controlling interest in one of crypto's most-trafficked data properties and gives CoinGecko resources to build out market-intelligence and trading products. It deepens Solana's institutional footprint at a moment when the network is actively pitching itself to TradFi, and puts a neutral-brand data platform inside an ecosystem player's portfolio. [`coindesk`](https://www.coindesk.com/business/2026/11/17/solana-foundation-takes-majority-stake-in-crypto-data-provider-coingecko) [`decrypt`](https://decrypt.co/383401/solana-foundation-backs-coingecko-eyes-trading)
{: #solana-foundation-takes-a-majority-stake-in-coingecko-as-the-data-aggregator-eyes-trading}

> **World Bank, Circle and Citi begin piloting USDC rails for development fund disbursements.** The initiative will test an intermediated, interoperable stablecoin model for getting money to recipients faster and more cheaply than traditional correspondent-banking routes. If it clears the pilot stage, it represents a meaningful institutional validation of USDC as settlement infrastructure rather than just a trading vehicle. [`theblock`](https://www.theblock.co/news/business/2026-11-17-world-bank-group-citi-circle-fund-disbursements-442924) [`decrypt`](https://decrypt.co/383485/world-bank-circle-citi-test-stablecoins-development-payments)
{: #world-bank-circle-and-citi-begin-piloting-usdc-rails-for-development-fund-disbursements}

> **Coinbase extends onchain crypto loans to New York via Morpho, with BTC, ETH and SOL as collateral.** New York has been a persistent holdout for many crypto product launches given its BitLicense regime, so the expansion is a signal that the regulatory path is now navigable. Borrowers put up crypto and receive USDC without a credit check; the protocol handles liquidation mechanics on-chain. [`theblock`](https://www.theblock.co/news/business/2026-11-17-coinbase-borrow-new-york-morpho-442842) [`theblock`](https://www.theblock.co/newsletters/the-daily/2026-11-18-ark-invest-crypto-stocks-nvidia-coinbase-loans-new-york-crypto-news-442902)
{: #coinbase-extends-onchain-crypto-loans-to-new-york-via-morpho-with-btc-eth-and-sol-as-collateral}

> **Ethereum's Glamsterdam upgrade could break up to 15,000 deployed contracts.** Core developers flagged on a recent call that two proposed scaling changes, which together would deliver a 3.3x capacity boost, violate assumptions baked into a large number of live contracts. The tension is a classic upgrade trilemma: meaningful throughput gains versus meaningful breakage risk for existing apps. No resolution date has been set. [`coindesk`](https://www.coindesk.com/tech/2026/11/17/ethereum-s-glamsterdam-upgrade-risks-breaking-up-to-15-000-contracts) [`decrypt`](https://decrypt.co/383462/ethereum-devs-scaling-upgrade-could-break-15000-apps)
{: #ethereums-glamsterdam-upgrade-could-break-up-to-15000-deployed-contracts}

<img class="section-card" id="security_desk" src="{{ "/assets/cards/2026-11-18-security_desk.png" | relative_url }}" alt="Security Desk" width="1200" height="300" loading="lazy" decoding="async">

> **Optimizely supply-chain attack hits 178 sites with wallet-draining and card-skimming malware.** Full write-up in the lead. TL;DR: audit your third-party script allowlists and enforce CSP. [`krebsonsecurity`](https://krebsonsecurity.com/2026/11/attackers-used-optimizely-to-a-b-test-malware-on-top-websites/)
{: #optimizely-supply-chain-attack-hits-178-sites-with-wallet-draining-and-card-skimming-malware}

> **Binance hack wallets move $137 million in ETH after a two-week dormancy.** A wallet tied to October's record Binance exploit shifted $63 million in ether, with analysts then flagging a broader wave totalling roughly $137 million across related addresses. Some funds were also swapped into Bitcoin. U.S. recovery efforts are ongoing. [`decrypt`](https://decrypt.co/383446/binance-hack-wallets-move-ethereum-after-two-weeks) [`coindesk`](https://www.coindesk.com/business/2026/11/17/binance-hacker-moves-usd63-million-in-stolen-ether-after-two-weeks-of-silence)
{: #binance-hack-wallets-move-137-million-in-eth-after-a-two-week-dormancy}

> **Lighter exchange reopens after a single trader's leaked API key drained roughly $5 million in USDC.** The incident was not a protocol exploit but an API-key compromise that routed funds through trade and internal-transfer paths that lacked adequate withdrawal controls. Lighter returned the full $5 million to the affected trader and has since reopened deposits and withdrawals. [`theblock`](https://www.theblock.co/news/defi/2026-11-17-lighter-reopens-withdrawals-after-traders-api-key-leak-returns-about-5-million-in-usdc-442113) [`cointelegraph_defi`](https://cointelegraph.com/news/lighter-incident-exposes-risks-beyond-withdrawal-controls)
{: #lighter-exchange-reopens-after-a-single-traders-leaked-api-key-drained-roughly-5-million-in-usdc}

> **SEAL weekly triage: 85 incidents logged in the past seven days.** Security Alliance's radar report covers losses by threat category and publishes IOCs for the week ending 17 November. No single dominant attack vector is called out, suggesting continued broad-based opportunistic activity. [`seal_radar`](https://radar.securityalliance.org/seal-weekly-stats-11-17-2026/)
{: #seal-weekly-triage-85-incidents-logged-in-the-past-seven-days}

<img class="section-card" id="on_the_hill" src="{{ "/assets/cards/2026-11-18-on_the_hill.png" | relative_url }}" alt="On the Hill" width="1200" height="300" loading="lazy" decoding="async">

> **Federal judge acquits MIT brothers in the $25 million Ethereum MEV case — ruling Ethereum has no terms of use.** Judge Jessica Clarke found prosecutors could not prove the material misrepresentation required for wire fraud, reasoning that because the Ethereum protocol has no terms of use, exploiting MEV ordering is not a false promise to any counterparty. The ruling comes a year after a jury deadlocked and does not adjudicate whether the conduct was ethical, only that it was not criminal under the wire fraud statute. It is the most consequential judicial statement on MEV legality to date. [`coindesk`](https://www.coindesk.com/policy/2026/11/18/u-s-judge-says-ethereum-has-no-terms-of-use-clears-mit-brothers-of-usd25-million-fraud) [`cointelegraph_regulation`](https://cointelegraph.com/news/us-judge-acquits-brothers-25m-ethereum-mev-exploit) [`decrypt`](https://decrypt.co/383408/judge-acquits-mit-brothers-in-25m-ethereum-mev-case-ending-prosecution)
{: #federal-judge-acquits-mit-brothers-in-the-25-million-ethereum-mev-case-ruling-ethereum-has-no-terms-of-use}

> **CFTC formally greenlights perpetuals in the US, with Backpack as the first approved venue.** Chairman Mike Selig framed the approval as a milestone and signalled more venues would follow. The move ends years of regulatory ambiguity around onshore perps and sets a compliance template for other platforms seeking CFTC authorisation. [`decrypt`](https://decrypt.co/383418/morning-minute-the-cftc-officially-greenlights-perps-in-the-us-starting-with-backpack)
{: #cftc-formally-greenlights-perpetuals-in-the-us-with-backpack-as-the-first-approved-venue}

> **Trump's CFTC nominees face Senate questions over prediction markets; Kalshi ordered to pause Trump-mention contracts.** Both nominees voiced scepticism about the public benefit of event contracts, with one saying the CFTC must weigh that question carefully. Separately, Kalshi has complied with a CFTC order to halt its Trump-mention markets while the regulator reviews manipulation risks, with a December 11 deadline to defend the contracts. [`coindesk`](https://www.coindesk.com/policy/2026/11/17/nominee-says-u-s-cftc-must-think-hard-about-public-benefit-of-prediction-markets) [`theblock`](https://www.theblock.co/news/regulation/2026-11-17-trumps-cftc-picks-face-senate-scrutiny-as-prediction-market-turf-war-heats-up-442909) [`cointelegraph_regulation`](https://cointelegraph.com/news/cftc-kalshi-trump-mention-markets-review) [`coindesk`](https://www.coindesk.com/policy/2026/11/17/predictions-platform-kalshi-complies-with-order-to-halt-trump-mention-contracts)
{: #trumps-cftc-nominees-face-senate-questions-over-prediction-markets-kalshi-ordered-to-pause-trump-mention-contracts}

> **Former Robinhood engineer pleads guilty to insider trading via Hyperliquid perps ahead of listing announcements.** Huaisong Xiang admitted using confidential knowledge of upcoming Robinhood token listings to trade perpetual futures on Hyperliquid, netting $125,523. He faces up to 20 years for wire fraud. The case establishes that classical insider-trading logic extends cleanly onto decentralised derivatives venues. [`theblock`](https://www.theblock.co/news/regulation/2026-11-17-former-robinhood-engineer-pleads-guilty-to-wire-fraud-over-trades-ahead-of-crypto-listing-announcements-442106) [`cointelegraph_regulation`](https://cointelegraph.com/news/ex-robinhood-engineer-pleads-guilty-125k-crypto-trading-fraud) [`decrypt`](https://decrypt.co/383443/former-robinhood-engineer-pleads-guilty-crypto-insider-trading)
{: #former-robinhood-engineer-pleads-guilty-to-insider-trading-via-hyperliquid-perps-ahead-of-listing-announcements}

## What else is grinding?
{: .brewing-label}

- Wells Fargo more than doubled its reported BlackRock bitcoin ETF position to $2.35 billion, or 49.6 million shares, in the latest 13-F filing. [`coindesk`](https://www.coindesk.com/markets/2026/11/17/wells-fargo-s-reported-blackrock-bitcoin-etf-holdings-double-to-usd2-35-billion) [`cryptobriefing`](https://cryptobriefing.com/wells-fargo-doubles-blackrock-bitcoin-etf-stake/)
- ARK Invest rotated $85 million out of Nvidia ahead of earnings and deployed roughly $40 million into Block, Circle and Coinbase during Monday's selloff. [`decrypt`](https://decrypt.co/383463/cathie-wood-ark-sells-85-million-nvidia-buys-crypto-stocks)
- Coin Center filed a comment to the SEC arguing that publishing open-source code is protected speech and that independent developers should not become regulated venues merely because others adopt their software. [`coincenter`](https://coincenter.org/comment-of-coin-center-to-the-securities-and-exchange-commission-on-order-granting-temporary-conditional-exemptive-relief/)
- Stablecoin infrastructure firm Avenia closed a $25 million Series A extension led by Lightspeed Faction, bringing total funding to $44.6 million. [`theblock`](https://www.theblock.co/news/deals/2026-11-17-avenia-funding-stablecoin-crypto-infrastructure-442119)
- Four Democratic senators sent the SEC a letter asking who would bear AML responsibility for tokenized shares transferred outside regulated platforms and whether those tokens could be frozen or recovered. [`cointelegraph_regulation`](https://cointelegraph.com/news/us-senators-sec-tokenized-stock-safeguards)
- Crypto unicorns from the 2021 vintage are now trading at 50% to 70% discounts in secondary markets, even as the top-tier names hit new highs. [`theblock`](https://www.theblock.co/newsletters/the-funding/2026-11-17-crypto-startup-valuations-442903) [`cryptobriefing`](https://cryptobriefing.com/crypto-unicorns-from-2021-boom-see-50-70-markdowns-in-secondary-markets/)

---

> **Last sip.** The MEV acquittal clears two defendants but leaves the broader question of what, if anything, Ethereum's permissionless ordering rules protect — and who gets to answer that next.
{: .last-sip}
