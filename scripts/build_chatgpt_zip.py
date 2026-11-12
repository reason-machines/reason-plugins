#!/usr/bin/env python3
"""Build the ChatGPT/Codex plugin directory ZIP from plugins/reason.

The ZIP holds only the portable Agent Plugins package: plugin.json, mcp.json,
skills/ and assets/. The Cursor, Claude and Codex compatibility files stay out,
because the portal reads the portable root manifest and rejects packages with
app references or lifecycle hooks.

plugin.json carries no `review.test_cases`. Per the submission guide, "Omitting
`test_cases`, or setting it to null, preserves existing cases; `test_cases`: {}
clears both lists." The build refuses a manifest that declares test cases, so
it cannot replace or clear the cases saved in the portal draft.
https://developers.openai.com/plugins/deploy/submission#configure-onboarding-review-and-publication

Usage: python3 scripts/build_chatgpt_zip.py [output.zip]
"""
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/reason'
CONTENTS = ['plugin.json', 'mcp.json', 'skills', 'assets']
# Fixed timestamp so the same sources always produce the same bytes.
EPOCH = (2026, 1, 1, 0, 0, 0)


def files():
    for name in CONTENTS:
        path = PLUGIN / name
        if path.is_file():
            yield path
        else:
            yield from sorted(p for p in path.rglob('*') if p.is_file() and p.name != '.DS_Store')


def check_review(manifest):
    review = manifest.get('extensions', {}).get('com.openai', {}).get('review') or {}
    if review.get('test_cases') is not None:
        raise SystemExit('plugin.json declares review.test_cases; an upload would replace '
                         'or clear the cases saved in the portal draft. Remove them.')


def build(output):
    check_review(json.loads((PLUGIN / 'plugin.json').read_text()))
    output = Path(output)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files():
            info = zipfile.ZipInfo(path.relative_to(PLUGIN).as_posix(), EPOCH)
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes(), zipfile.ZIP_DEFLATED)
    return output


if __name__ == '__main__':
    out = build(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'reason-chatgpt.zip')
    with zipfile.ZipFile(out) as archive:
        print(f'{out}: {len(archive.namelist())} files')
        for name in archive.namelist():
            print('  ' + name)
