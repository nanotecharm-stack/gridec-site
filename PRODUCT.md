# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary: the owner of a business or facility in Armenia, who is not an engineer.**
Something on the site is failing, tripping, overheating or costing more than it should,
and they have to decide whether measuring it is worth the money. They judge the service
by consequences, not by method. Copy is written for this person first: the page must
explain what may be happening and what they would get, without requiring them to read a
technical argument.

The page must also survive readers who arrive later in the same decision, and must not be
written in a way that embarrasses the primary reader in front of them:

- engineers and contractors, who check whether the method is credible;
- banks, investors and EPC or project partners, who need an independent assessment before
  a purchase, a commissioning or a financing decision;
- solar plant owners, whose stations underperform or whose inverters disconnect;
- owners of commercial and premium private property.

## Product Purpose

The company records how an electrical network actually behaves under working load,
analyses the recording, and issues an engineering conclusion based on the measured data.

The core service is a **seven-day power quality measurement under working load**: an
analyser is installed on site, electrical parameters and power quality events are recorded
over time, deviations are analysed, and a technical report is produced.

The reason the service exists: electrical problems are frequently invisible during a short
inspection. Lights work, equipment starts, breakers do not trip — and the network still
has voltage dips, unbalance, harmonic distortion, overloads or unstable protection
behaviour. Some events last milliseconds; by the time anyone inspects, the values look
normal again.

Success for the visitor is understanding whether their electrical conditions may be
affecting equipment, cost, reliability or a project decision — and having measured
evidence instead of an assumption.

## Positioning

The company moves a question from assumption to measured fact, and stops there. It is an
**engineering diagnostics** practice: it measures, analyses and concludes.

What it is deliberately not, and must never be presented as:

- an electrical installation contractor;
- an equipment reseller or a manufacturer's official representative;
- a generic energy consultant;
- a legal-dispute service;
- a replacement for a designer, contractor, supplier or lawyer.

It does not guarantee that a problem will be solved. It provides monitoring, analysis and
technical findings based on measured data.

## Operating Context

Typical situations that bring a visitor to the page:

- unstable equipment operation, repeated faults, unexplained shutdowns;
- overheating, voltage drops, phase imbalance, suspected power quality issues;
- checking a facility before purchase;
- checking a facility before commissioning;
- a solar plant producing less than expected;
- supporting a technical discussion between owner, contractor, bank, investor or partner.

The deliverable that ends the engagement is a written report separating measured facts
from engineering interpretation and recommendation.

## Capabilities and Constraints

- **Languages: English and Armenian now; Russian is planned later.** Layout and type
  choices must therefore hold Cyrillic from the start, not be retrofitted. (The older
  `SITE_BRIEF.md` line "Russian only, first version" is superseded by this.)
- Armenian is a first-class language, not a translation afterthought: it has its own
  terminology decisions and its own forbidden words, already applied in the build.
- One page, static, no backend. The enquiry form posts to a third-party form service.
- Measurement methodology referenced on the site: **IEC 61000-4-30 Class S**. Reference
  standard for limits: **EN 50160**. No instrument class beyond Class S may be claimed.
- **The company name is settled: Gridec.** "PowerTech" failed a name check; the
  candidates once under consideration (Metrion, Attesta, Stuyg) are closed. The legal
  form used on the page is **Gridec LLC**. The name is already built in everywhere —
  wordmark, page title, metadata, the mark, and every occurrence in copy.
- **Identity is decided and implemented.** Palette: blue (accent `#2E5E99` on paper,
  `#7BA4D0` on the plates, ink `#0D2440`, warm paper `#F6F1E9`, warm text ink `#2B2722`).
  Mark: the outlined cube, single-colour — blue on light grounds, light on dark ones.
  Wordmark: Oxanium 600, drawn as curves so no font ships for it. Binding visual
  constraints agreed with the owner live in `CLAUDE.md` and `SITE_BRIEF.md`; the
  implemented system lives in the code under `powertech-v2-build/` and is not yet written
  up as a DESIGN.md.
- **The domain is not bought yet.** Anything needing an absolute URL is therefore
  deferred: `og:url`, `og:image`, and lifting `robots: noindex,nofollow` from the deploy
  build. The email on the page is still `sales@powertech.am`.

## Brand Commitments

**Voice.** Technically competent people explaining an engineering service in plain
language. Calm, precise, technically correct. Understandable to a facility owner,
credible to an engineer, and presentable to a bank or an international partner. Not
aggressive, not corporate-heavy, not loaded with jargon.

**Calls to action stay invitational**, in the owner's own wording: discuss the site, see
how the check works, send an enquiry, tell us what is happening at the facility. Pressure
wording is forbidden: order now, get a discount, urgent diagnostics, do not lose money,
best in Armenia.

**Claims discipline is a brand commitment, not a legal footnote.** The credibility of a
diagnostics practice is the whole product; a single invented fact destroys it.

## Evidence on Hand

What genuinely exists and may be used:

- the measurement methodology and the standards named above;
- a 2026 market-intelligence document behind the sector-economics content, whose
  third-party figures may be used **only with attribution to their source**;
- the owner's own authored copy for the sector modal and the contact section.

What does **not** exist and must never be fabricated — confirmed again on 2026-08-01:

- no named clients, no case studies, no completed-project references;
- no certifications, licences, awards or years of experience;
- no official partnership, and **no equipment manufacturer named on the site**;
- no prices and no guarantees;
- no sample report to publish.

The site therefore earns trust through method, clarity and restraint, not through proof
it does not have. When new evidence becomes available, it is added here first and only
then to the page.

## Product Principles

1. **Measured, or not said.** Every claim traces to a measurement, a named standard or an
   attributed source. Absence of evidence is stated plainly, never papered over.
2. **The owner reads first, the engineer audits second.** Plain-language consequence
   before technical method — but the technical method must be there and must be right.
3. **The conclusion is the product.** The service ends in a report a third party can act
   on; the site's job is to make that deliverable understandable and credible.
4. **Restraint is the credibility signal.** In this market, a quiet, precise page reads as
   competence; a loud one reads as a sales operation with nothing measured behind it.
5. **Armenian carries equal weight.** A decision that works only in English is not
   finished.

## Accessibility & Inclusion

- Text contrast is held to WCAG AA and verified numerically, not by eye. This has already
  driven real product decisions: the accent colour was darkened for small text because the
  brand colour measured 3.46:1.
- Motion respects `prefers-reduced-motion`.
- The page must remain usable on a phone in the field, where a facility owner is likely to
  open it first.
