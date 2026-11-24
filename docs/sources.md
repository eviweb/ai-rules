# Sources register

External references that ai-rules relies on: standards, regulations, published guidance and the upstream project some skills are derived from. Each row records the version actually used, where to check it, when it was last checked and how often it should be checked again. `scripts/check-sources-age.sh` lists the rows that are due, and a monthly workflow opens an issue when there are any (it never blocks a merge).

Status: `verified` (read at its official source on the date given), `to confirm` (a detail could not be read), `not checked` (cited from knowledge, never checked against the source). A row with `never` as its date counts as due.

When a row is checked, update its version, date and status in the same commit as any text change it causes.

| Source | Version used | Reference | Verified | Every (months) | Status | Cited in |
|--------|--------------|-----------|----------|----------------|--------|----------|
| WCAG | 2.2 (W3C Recommendation, 2024-12-12) | https://www.w3.org/TR/WCAG22/ | 2026-11-24 | 12 | verified | quality-dimensions: accessibility |
| RGAA | 4.1.2, built on WCAG 2.1; version 5 announced for late 2026 | https://accessibilite.numerique.gouv.fr/ | 2026-11-24 | 6 | verified | quality-dimensions: accessibility |
| EN 301 549 | V2.1.2 as quoted by the RGAA references page | https://accessibilite.numerique.gouv.fr/ressources/references/ | 2026-11-24 | 12 | to confirm | quality-dimensions: accessibility |
| European Accessibility Act (Directive (EU) 2019/882) | applies from 28 June 2025 to products placed on the market and services provided after that date, with transition periods (read in the EUR-Lex summary; the full text page returned nothing) | https://eur-lex.europa.eu/eli/dir/2019/882/oj/eng | 2026-11-24 | 12 | verified | quality-dimensions: accessibility |
| Section 508 (US) | 2017 refresh, harmonised with WCAG 2.0 (level not stated on the page) | https://www.section508.gov/manage/laws-and-policies/ | 2026-11-24 | 12 | verified | quality-dimensions: accessibility |
| GDPR (Regulation (EU) 2016/679) | articles 5, 25, 33, 35 | https://gdpr-info.eu/ | 2026-11-24 | 12 | verified | quality-dimensions: privacy by design |
| Privacy by Design (Cavoukian) | seven foundational principles; six names seen in IPC documents, the primary document and the wording of the seventh were not read | https://www.ipc.on.ca/ | 2026-11-24 | 3 | to confirm | quality-dimensions: privacy by design |
| OWASP Top 10 | 2025 | https://owasp.org/www-project-top-ten/ | 2026-11-24 | 12 | verified | quality-dimensions: security by design |
| OWASP ASVS | 5.0.0 | https://asvs.owasp.org/ | 2026-11-24 | 12 | verified | quality-dimensions: security by design |
| OWASP API Security Top 10 | 2023 | https://api-security.owasp.org/ | 2026-11-24 | 12 | verified | quality-dimensions: security by design |
| Saltzer and Schroeder, design principles | 1975 paper, eight principles (section I.A.3) | https://web.mit.edu/Saltzer/www/publications/protection/Basic.html | 2026-11-24 | 60 | verified | quality-dimensions: security by design |
| Shostack, four-question threat modelling | four questions as worded on the site | https://shostack.org/resources/threat-modeling | 2026-11-24 | 24 | verified | quality-dimensions: security by design |
| SLSA (supply-chain levels) | 1.2 (Build track L0 to L3, Source track) | https://slsa.dev/spec/ | 2026-11-24 | 12 | verified | quality-dimensions: security by design |
| ISO/IEC 25010 | edition 2, published November 2023, nine characteristics (ISO catalogue; the names were read on iso25000.com) | https://www.iso.org/standard/78176.html | 2026-11-24 | 12 | verified | quality-dimensions: ISO mapping |
| ISO 9241-210 | 2019 (edition 2), confirmed on review (ISO catalogue) | https://www.iso.org/standard/77520.html | 2026-11-24 | 12 | verified | quality-dimensions: user-centric |
| Nielsen, usability heuristics | ten heuristics, page reviewed 2024-01-30 | https://www.nngroup.com/articles/ten-usability-heuristics/ | 2026-11-24 | 36 | verified | quality-dimensions: user-centric |
| DORA metrics | five metrics (guide updated 2026-01-05): change lead time, deployment frequency, failed deployment recovery time, change fail rate, deployment rework rate | https://dora.dev/guides/dora-metrics/ | 2026-11-24 | 12 | verified | quality-dimensions: reliability, evolvability |
| Conventional Commits | 1.0.0 | https://www.conventionalcommits.org/en/v1.0.0/ | 2026-11-24 | 24 | verified | core: commits |
| Keep a Changelog | 1.1.0 | https://keepachangelog.com/en/1.1.0/ | 2026-11-24 | 24 | verified | rules: changelog |
| Semantic Versioning | 2.0.0 | https://semver.org/ | 2026-11-24 | 24 | verified | rules: versioning |
| Superpowers (obra/superpowers) | v7.0.2 @ 22f0b46 | https://github.com/obra/superpowers | 2026-11-24 | 3 | verified | skills derived from it (see `THIRD_PARTY.md`) |

## Superpowers

The pinned commit in the "Version used" column is compared with the latest upstream commit by `scripts/check-sources-age.sh --check-upstream`. When upstream has moved, review the diff of the skills derived from it, rewrite what is worth keeping, then update the pin in each skill's `derived-from` and in this row.
