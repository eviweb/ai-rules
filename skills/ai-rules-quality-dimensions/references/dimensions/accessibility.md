# Accessibility
The system can be used by people with different abilities, devices and situations.

- Target WCAG 2.2 level AA for any interface; the four principles are perceivable, operable, understandable, robust
- Semantic structure first, ARIA only when native elements are not enough
- Keyboard-only operation, visible focus, sufficient contrast, text alternatives, no information carried by colour alone
- For CLI and TUI: readable without colour (`NO_COLOR`), plain-text and line-oriented output, no required mouse
- Test with keyboard, zoom and a screen reader, not only with automated checks
- Checklists by medium and legal references (RGAA, European Accessibility Act): [accessibility](../contexts/accessibility.md)

Red flags: mouse-only actions, colour as the only signal, unlabelled controls, motion that cannot be disabled, contrast never measured.
