# Safety
The system avoids states that could harm people, property or the environment.

- Identify hazards at design time, including destructive automation (scripts that delete data or change production)
- Fail safe: on error or doubt the system stops or reverts to the harmless state
- Limit the blast radius: confirmation, dry run, rate and size limits, scoped credentials
- Keep a human override and make hazards visible (clear warnings, not buried logs)
- Applies strongly to devices, health, vehicles and industrial control; in other projects, mainly to automation with irreversible effects

Red flags: irreversible actions without a preview, no emergency stop, unsafe defaults, warnings that nobody sees.
