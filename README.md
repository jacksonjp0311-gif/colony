<div align="center">

![Colony demo](docs/demo/banner.gif)

![Colony architecture](docs/architecture.png)

# Colony

**A swarm that prices a question before it answers it.**

*Forked and turned into an evolving runner by [James Paul Jackson](https://github.com/jacksonjp0311-gif). Original claim hygiene, cluster map, and independent verifier stay. Agents can now propose safe mutations to allocation and judgment knobs under twin control + Oracle gates. See [CHARTER.md](CHARTER.md) and `python -m colony.evolve`.*

[![tests](https://img.shields.io/badge/tests-54_passing-3fb950?style=flat-square)](tests/)
[![python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-8b949e?style=flat-square)](LICENSE)
[![mission](https://img.shields.io/badge/mission-03_Institutional_Markets-7c4dff?style=flat-square)](docs/MISSIONS.md)
[![telegraph](https://img.shields.io/badge/telegraph-season_II-0b0d12?style=flat-square)](https://telegraphprotocol.com)
[![rail](https://img.shields.io/badge/rail-x402_escrow-7cc4ff?style=flat-square)](docs/USAGE.md)
[![demo](https://img.shields.io/badge/demo-3m31s-ee8282?style=flat-square)](docs/demo/colony-demo.mp4)

</div>

Colony answers one commercial question, **is this counterparty safe for 60-day
payment terms**, by splitting it into seven claims, buying the cheapest Telegraph
answer that can settle each one, and printing a decision where every sentence is either
footnoted or absent.

The default is one ask per claim. Extra scouts are bought only where two sources already
disagree, or where a load-bearing claim came back dead. On a live run that was
**11 asks, 9 paid, $0.09**.

---

## Evolving runner (this fork)

Scheduled cycles (`.github/workflows/colony-evolve.yml`) run hard benches, then N evolve cycles. Each cycle measures the current knobs on a seed set, proposes one closed-set mutation, re-measures, and keeps only if the trial is strictly better *and* the twin control does not lead. The independent verifier is outside the mutation set. Human authorize remains required for durable accepts or new claims.

```bash
python -m colony.evolve --cycles 3
python -m colony.evolve --status
```

See [CHARTER.md](CHARTER.md), [society/LEARNING.md](society/LEARNING.md), and the original Athar surfaces below.

---

## The problem

Every credit decision ends the same way: a confident yes, and no record of which fact the
yes depended on. A $40/seat report arrives quarterly. A sanctions check gets run by hand.
The judgement itself is never written down.

Ask a model instead and you get the same shape of answer, minus the ability to check it.

## Why it is built this way

Telegraph ranks miners, so the network already gives you a good answer at 1x cost. Buying
three answers for every request is a tax, not verification. Colony spends the first dollar
on **coverage** (one claim at a time) and the second only on **the claim the verdict hinges
on**.

| Run | Claims | Asks | Paid | Cost |
|---|---|---|---|---|
| Maersk, full decision | 7 | 11 | 9 | **$0.09** |
| Maersk, coverage only | 7 | 7 | 6 | **$0.06** |

## The loop

```
plan      seven claims, most load-bearing first, until the budget is committed
scout     one claim, one miner, one fact, one receipt; a broken miner fails over
map       settled / contested / blind / dead, per claim
escalate  at most 2 claims, at most 2 extra scouts: contested or dead load-bearing only
verdict   ALLOW / ALLOW WITH CONDITIONS / HOLD / BLOCK, read from the map alone
memo      footnotes, a receipt table, and what could not be verified
```

The queen reads the map, never a raw answer, so one confident scout cannot decide
anything on its own.

## What a decision looks like

```
# A.P. Moller-Maersk A/S

**Verdict: ALLOW WITH CONDITIONS** · confidence 50/100 · spent $0.0900 on 9 purchases

- no sanctions match reported by the sources that answered
- registry reports the entity as active

## What the swarm bought

- **sanctions** (settled) — matched: False [1],[8],[9]
- **registry** (single) — legal_name: A.P. MØLLER - MÆRSK A/S; registration_id: 22756214; active: True [2]
- **filings**  (single) — filing_count: 0 [3]
- **identity** (single) — company: maersk.com; industry: Maersk [4]
- **news**     (single) — result_count: 4 [5]
- **macro**    (single) — rate_pct: 5.529 [6]
- **fx**       (single) — converted_amount: 6,801.2739 [7]

## What we could not verify

Nothing was left unverified in the claims this budget covered.
```

Confidence is 50 rather than 100 because most secondary claims were single-sourced, and
the memo says so instead of implying corroboration.

## Quickstart

```bash
git clone https://github.com/jacksonjp0311-gif/colony && cd colony
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m pytest tests -q          # 54 tests, offline, no wallet
```

Free, no spend:

```bash
./.venv/bin/python -m colony claims            # the seven claims and their intents
./.venv/bin/python -m colony ledger            # purchases so far, with receipts
./.venv/bin/python scripts/verify_bundle.py evidence/colony-maersk-20261121.json
```

A paid decision, about nine cents on testnet:

```bash
./.venv/bin/python -m colony ask "Is this counterparty safe for 60-day terms?" \
  --company "A.P. Moller-Maersk A/S" --domain maersk.com --budget 0.25 \
  --bundle runs/demo.json --live
```

HTTP, for anything that is not a human:

```bash
./.venv/bin/python -m colony.api --port 8088
curl -s localhost:8088/ask -H 'content-type: application/json' \
  -d '{"company":"A.P. Moller-Maersk A/S","budget_usd":0.25}' | jq '.verdict'
```

## Verify, do not trust

Every run writes a bundle: every fact, every receipt, every price, and one sha256 over
the canonical payload.

```
$ python scripts/verify_bundle.py evidence/colony-maersk-20261121.json
  ok  hash ok: cee82b5a8e9e4e4b
  ok  ledger: 11 entries cover 7 claims
  ok  receipts: 8 present, 3 asks failed
VERIFIED
```

Change one fact in a copy and the same command prints `TAMPERED`. The verifier never
imports the code that produced the file.

## What it does not do

- It does not verify claims it could not buy. They appear under "what we could not verify".
- It does not average disagreements. Both sides are shown; neither is chosen.
- It does not run on mainnet, and makes no claim about production pricing.
- It does not decide for you. `HOLD` means a human should look, not guilty.

## Built on Telegraph

Telegraph is a market for answers. Each kind of question is an **intent**, independent
**miners** compete to serve it and are ranked by performance, and payment settles per
answer through an escrow rail. Every answer returns a receipt hash and a signal hash the
payer can resolve on the node.

Colony buys seven intents per decision: `SANCTIONS_SCREENING_MATCH_GENERAL`,
`CORPORATE_REGISTRY_LOOKUP_GENERAL`, `REGULATORY_FILING_MONITOR_GENERAL`,
`B2B_IDENTITY_ENRICHMENT_GENERAL`, `NEWS_SEARCH_GENERAL`,
`MACRO_ECONOMIC_INDICATOR_GENERAL`, `CURRENCY_EXCHANGE_CONVERT`.

## Layout

```
colony/intents.py    the seven claims and how each maps to an intent
colony/scouts.py     one claim, one ask, one fact, with failover
colony/cluster.py    agreement, disagreement, blindness
colony/allocator.py  coverage first, escalation where it pays
colony/queen.py      the loop and the verdict rules
colony/memo.py       the footnoted document and the signed bundle
colony/ledger.py     append-only purchases
colony/policy.py     budget and caps
colony/cli.py        ask, watch, ledger, claims
colony/api.py        POST /ask
colony/evolve.py     cyclic runner (this fork)
colony/knobs.py      closed set of safe mutable parameters
scripts/             fund_testnet, verify_bundle, tamper, verify_evidence
evidence/            real runs, probes, receipts
truth/               evaluation material contributed to the pool
society/             LEARNING.md and evolve surfaces
```

## Documentation

- [Product](docs/PRODUCT.md) - the customer, the job, the cut list
- [Positioning](docs/POSITIONING.md) - what it replaces, and the honest limits
- [Pricing](docs/PRICING.md) - measured cost per decision
- [Decisions](docs/DECISIONS.md) - why v2 was thrown away
- [Usage](docs/USAGE.md) - one decision end to end
- [Troubleshooting](docs/TROUBLESHOOTING.md) - every failure these runs hit
- [Evidence index](docs/EVIDENCE.md) - five minutes for a reviewer
- [CHARTER](CHARTER.md) - hard ceiling for the evolving runner

## Status

Testnet only. 93 commits, 54 tests, 11 paid asks in the committed run, one mission
(Mission 03, Institutional Markets) with macro and FX bought as supporting claims. No
miner shipped yet.

This fork adds the evolve runner skeleton. Real measurement against seed counterparties and a full Oracle still to be wired.

MIT. See [LICENSE](LICENSE).

<div align="center">

Original by [Athar](https://github.com/atharhive) · Evolving runner by [James](https://github.com/jacksonjp0311-gif)

</div>
