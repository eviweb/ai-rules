# Privacy & data minimisation
The system collects, stores, and processes only the data strictly necessary for its purpose.

- Identify personal data at design time — document what is collected and why
- Apply retention limits: delete or anonymise data when it is no longer needed
- Do not log PII (names, emails, IP addresses, user identifiers) unless explicitly required and documented
- Provide a way to delete user data on request (right to erasure)
- Apply data minimisation at every layer: API responses, database queries, log entries

- Principles, GDPR articles and checklist: [privacy by design](../contexts/privacy-by-design.md)

Red flags: logging full request bodies that may contain PII, no data retention policy, storing data "just in case", third-party analytics that collect more than needed.
