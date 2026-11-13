# Install Simulation

- OK: `False`
- Package directory: `/Users/ling99/Codexfiles/Codex/lyz-skills/lyz-aircraft-embroidery/dist`
- Archive extracted: `True`
- Entrypoint loaded: `True`
- Manifest loaded: `True`
- Interface loaded: `True`
- Adapters readable: `1`
- Installer permissions enforced: `0`
- Installer permission failures: `3`
- Failures: `3`
- Warnings: `0`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `archive-present` | `pass` | Package archive exists: /Users/ling99/Codexfiles/Codex/lyz-skills/lyz-aircraft-embroidery/dist/lyz-aircraft-embroidery.zip |
| `archive-safe-paths` | `pass` | Archive has no absolute or parent-traversal entries |
| `single-top-level` | `pass` | Archive top-level directory is lyz-aircraft-embroidery |
| `entrypoint-load` | `pass` | Installed SKILL.md frontmatter is readable |
| `entrypoint-name` | `pass` | Installed SKILL.md name matches package directory |
| `entrypoint-description` | `pass` | Installed SKILL.md description is present |
| `manifest-load` | `pass` | Installed manifest.json is readable |
| `manifest-name` | `pass` | Installed manifest name matches package manifest |
| `manifest-version` | `pass` | Installed manifest version matches package manifest |
| `interface-load` | `pass` | Installed agents/interface.yaml is readable |
| `overview-report` | `pass` | Installed overview report is present |
| `review-studio-report` | `pass` | Installed Review Studio report is present |
| `adapter-openai` | `pass` | openai adapter is readable after package install simulation |
| `adapter-openai-name` | `pass` | openai adapter name matches package manifest |
| `permission-policy-load` | `fail` | Installed permission policy is readable |
| `permission-openai-contract` | `pass` | openai adapter exposes target permission contract for installer enforcement |
| `permission-openai-file_write-approved` | `fail` | openai capability file_write has active reviewer approval |
| `permission-openai-file_write-target-enforcement` | `fail` | openai capability file_write has target enforcement note |

## Failures

- Installed permission policy is readable
- openai capability file_write has active reviewer approval
- openai capability file_write has target enforcement note

## Warnings

- None
