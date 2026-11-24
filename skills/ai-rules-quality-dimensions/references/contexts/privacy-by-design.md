# Privacy by design

Read when the project handles personal data: accounts, emails, names, IP addresses, device or location data, logs that contain identifiers. This is engineering guidance, not legal advice; ask the user which jurisdiction and regulations apply (for example the GDPR in the EU) and whether a data protection officer exists.

## Seven foundational principles (Cavoukian)

1. **Proactive, not reactive**: prevent privacy harm at design time.
2. **Privacy as the default**: the most protective setting without any user action.
3. **Embedded in the design**: part of the architecture, not an add-on.
4. **Full functionality**: privacy and function together, not a trade.
5. **End-to-end security**: protection across the whole lifecycle of the data.
6. **Visibility and transparency**: users can see what happens to their data.
7. **Respect for the user**: keep it user-centric, with clear choices and control.

## GDPR principles to design for (art. 5 and 25)

- Lawfulness, fairness, transparency; **purpose limitation**; **data minimisation**; accuracy; **storage limitation**; integrity and confidentiality; accountability.
- **Data protection by design and by default** (art. 25): the defaults collect and expose the minimum.
- Rights to build in: access, rectification, erasure, portability, objection. Breach notification within 72 hours (art. 33). A data protection impact assessment for high-risk processing (art. 35).

## Practice

1. **Inventory**: list each data item, why it is collected, where it is stored, who can read it, how long it is kept. If no purpose, do not collect it.
2. **Minimise**: collect less, truncate or hash identifiers, pseudonymise or anonymise when the purpose allows, avoid free-text fields that invite sensitive data.
3. **Retain**: a retention period per item and a job that enforces it; deletion that really deletes (including backups on a schedule).
4. **Protect**: encryption in transit and at rest, least-privilege access, separation of identifiers from content.
5. **Logs and analytics**: no personal data in logs (`rules/logging.md`), no third-party SDK or tracker without a purpose and a decision from the user; prefer privacy-friendly analytics.
6. **Test data**: never use real personal data in tests, fixtures or screenshots.
7. **Third parties and transfers**: know the processors, the contracts and where the data goes.
8. **Consent and notice**: clear, specific, as easy to withdraw as to give; no dark patterns.

## Red flags

Data collected "just in case", identifiers in URLs and logs, no deletion path, production data in development, analytics added by default.
