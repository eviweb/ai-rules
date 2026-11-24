# Example comparison

A tool that reads a registry of agents and installs rule files for each (the shape of ai-rules itself). Illustrative: ratings come from the project's criteria, not from the style.

Context: one maintainer, Python 3.11+, CLI only, about ten commands, five agents today and more expected, must run on Ubuntu LTS and Termux, no network, no personal data, must be testable without touching the real home directory.

| Criterion | A. Single script | B. Library + thin CLI | C. Hexagonal |
|-----------|------------------|-----------------------|--------------|
| Effort to build | ++ | + | - |
| Testability (no real filesystem) | - | + | ++ |
| Adding the sixth agent | - (edit branching code) | + (new registry entry) | + |
| Operational burden | ++ | ++ | ++ |
| Fit with a single maintainer | ++ | + | 0 (more files to hold) |
| Reversibility | ++ | ++ | + |
| Portability (Termux) | + | + | + |

**Recommendation:** B. The registry removes agent-specific branching, the library core is testable with temporary directories, and a single maintainer does not need ports and adapters for one interface and one storage.

**Would change the recommendation:** a second interface (an API or a TUI) appears, or storage other than the filesystem is needed: then extract ports, i.e. move toward C.

**First slice:** one agent end to end (`install`, `status`, `remove`) with its tests, then the registry for the others.

**Quality scenarios:** adding a sixth agent touches one registry entry and one test file and takes under an hour; the whole suite runs in under ten seconds without touching the real home directory.

**Riskiest assumption:** that the registry can describe every agent's install steps without agent-specific code. Checked with a spike on the two most different agents before building the rest.

**Exit plan:** the library core has no CLI dependency, so replacing the command layer (for another framework) touches one module.
