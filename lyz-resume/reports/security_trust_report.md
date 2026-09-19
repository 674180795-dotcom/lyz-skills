# Security Trust Report

- OK: `True`
- Scanned files: `36`
- Scripts: `8`
- Internal script modules: `0`
- Secret findings: `0`
- Network-capable scripts: `0`
- Network policy covered scripts: `0`
- Network policy missing scripts: `0`
- File-write scripts: `8`
- Permission approvals: `2 / 2`
- Permission approval gaps: `0`
- CLI help smoke checked: `8`
- CLI help smoke failures: `0`
- Interactive scripts: `0`
- Package hash scope: `source-contract-without-generated-reports`
- Package hash files: `36`
- Package SHA256: `2a96cf96b47ed4be34e0924b62ba8ecde1be2d3e887293ce2f8abdffc52f6670`

## Failures

- None

## Warnings

- None

## Dependency Evidence

- Files: `requirements.txt`
- Pinned entries: `0`
- Unpinned entries: `0`

## Network Policy

- Policy file: `security/network_policy.json`
- Present: `False`
- Covered scripts: `0`
- Missing scripts: `none`
- Mismatches: `0`

## Permission Governance

- Policy file: `security/permission_policy.json`
- Present: `True`
- Required capabilities: `file_write, subprocess`
- Approved capabilities: `file_write, subprocess`
- Missing approvals: `none`
- Invalid approvals: `none`
- Expired approvals: `none`

## CLI Help Smoke

- Enabled: `True`
- Timeout seconds: `5.0`
- Checked scripts: `8`
- Passed scripts: `8`
- Failed scripts: `none`

## Script Surface

| Script | Interface | Declared | Argparse | Main Guard | Input | Network | File Write | Subprocess | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripts/assess_intake.py | cli | False | True | True | False | False | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/extract_resume.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/pdf_to_images.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/render_resume.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/render_resume_v2.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/validate_alignment.py | cli | False | True | True | False | False | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/validate_resume.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/validate_resume_v2.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
