# Accessibility

Read when the project has any interface: web, GUI, TUI or CLI, documentation, error output.

## Target and references

- **WCAG 2.2, level AA** is the default target. Four principles: **perceivable** (alternatives, contrast, adaptable), **operable** (keyboard, enough time, no seizures, navigable), **understandable** (readable, predictable, input help), **robust** (works with assistive technology).
- Legal frames to ask the user about: **RGAA** (France; version 4.1.2, which is built on WCAG 2.1; a version 5 was announced for late 2026; public services and large companies, with an accessibility statement), **EN 301 549** (EU), the **European Accessibility Act** (Directive (EU) 2019/882: transposition was due in June 2022; requirements for many consumer products and services apply from June 2025, to be confirmed on EUR-Lex), Section 508 (US). Ask which apply; do not assume.
- RGAA is based on WCAG 2.1: the WCAG 2.2 criteria below are good practice that RGAA does not yet require.

## Web

- Semantic HTML first: real headings in order, lists, landmarks, buttons for actions and links for navigation. **ARIA only when native elements cannot do the job**; wrong ARIA is worse than none.
- Every control has an accessible name (visible label, not placeholder alone). Errors are identified in text, linked to the field, with a suggestion to fix.
- Keyboard: everything reachable and operable, logical focus order, visible focus, no trap, skip link.
- Contrast: 4.5:1 for text (3:1 for large text and interface components). Never use colour alone to carry information.
- Text alternatives for images, captions for video, transcripts for audio; page language declared.
- Layout reflows at 320 px width and 400 % zoom; text spacing adjustable; touch targets at least 24 by 24 CSS pixels.
- Honour `prefers-reduced-motion`; no content that flashes more than three times a second.
- Authentication that does not require solving puzzles or remembering (WCAG 2.2); help in a consistent place.

## GUI and mobile

Use the platform accessibility API: names, roles and states for every control, keyboard and switch access, dynamic type, respect system contrast and motion settings.

## CLI and TUI

- Nothing meaningful by colour alone; honour `NO_COLOR` and `--no-color`.
- Line-oriented plain text works with screen readers; avoid redrawing the screen, cursor games and animated spinners when not on a terminal (`[ -t 1 ]`).
- A machine-readable output mode (`--json`) and a quiet mode help assistive tools.
- Errors say what went wrong and what to do, in words, not codes alone. Keep lines readable at narrow widths.

## Documentation

Headings in order, meaningful link text (not "click here"), alternative text for diagrams (describe the structure in words next to the diagram), code blocks with a language, no information only in screenshots.

## Verify

- Automated checks (axe, pa11y, Lighthouse) find a minority of problems: use them as a floor.
- Manual: keyboard only, 200 % zoom and narrow viewport, high-contrast mode, and a screen reader (NVDA, VoiceOver, Orca).
- Record the target level and known gaps in an accessibility statement when a public interface exists.
