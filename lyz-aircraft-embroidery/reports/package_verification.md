# Package Verification

- OK: `False`
- Package directory: `/Users/ling99/Codexfiles/Codex/lyz-skills/lyz-aircraft-embroidery/dist`
- Targets: `1 / 1` adapters present
- Archive present: `True`
- Archive SHA256: `a38213b173cd7abadad24117100f874a27d80751cd38ba6f186723686a1e0579`
- Failures: `1`
- Warnings: `0`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `package-manifest` | `pass` | Package manifest exists: /Users/ling99/Codexfiles/Codex/lyz-skills/lyz-aircraft-embroidery/dist/manifest.json |
| `openai-adapter` | `pass` | Adapter exists for target: openai |
| `archive-safe-paths` | `pass` | Archive has no absolute or parent-traversal entries |
| `archive-entry-lyz-aircraft-embroidery/SKILL.md` | `pass` | Archive contains lyz-aircraft-embroidery/SKILL.md |
| `archive-entry-lyz-aircraft-embroidery/manifest.json` | `pass` | Archive contains lyz-aircraft-embroidery/manifest.json |
| `archive-entry-lyz-aircraft-embroidery/agents/interface.yaml` | `pass` | Archive contains lyz-aircraft-embroidery/agents/interface.yaml |
| `archive-excludes-generated` | `pass` | Archive excludes generated dist/, .previews/, and tests/tmp* contents |
| `registry-ok` | `fail` | Registry audit is OK |
| `registry-name-match` | `pass` | Registry package name matches package manifest |
| `registry-version-match` | `pass` | Registry package version matches package manifest |
| `registry-compat-openai` | `pass` | Registry compatibility is reviewable for target: openai |

## Failures

- Registry audit is OK

## Warnings

- None
