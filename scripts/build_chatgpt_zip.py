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
import struct
import sys
from urllib.parse import urlsplit
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/reason'
CONTENTS = ['plugin.json', 'mcp.json', 'skills', 'assets']
# Fixed timestamp so the same sources always produce the same bytes.
EPOCH = (2026, 1, 1, 0, 0, 0)


LISTING_URLS = ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']
REQUIRED_TEXT = ['displayName', 'shortDescription', 'longDescription', 'developerName']
ICONS = ['composerIcon', 'logo', 'logoDark']
MAX_URL = 1024
MAX_ICON_SIDE = 4096
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def files(plugin=PLUGIN):
    """Yield the package files, refusing symlinks so nothing outside the plugin is archived."""
    root = plugin.resolve()
    for name in CONTENTS:
        path = plugin / name
        candidates = [path] if path.is_file() or path.is_symlink() else sorted(path.rglob('*'))
        for candidate in candidates:
            if candidate.is_symlink():
                raise SystemExit(f'{candidate.relative_to(plugin)} is a symlink; the package must hold real files.')
            if not candidate.is_file() or candidate.name == '.DS_Store':
                continue
            if root not in candidate.resolve().parents:
                raise SystemExit(f'{candidate} resolves outside {plugin}.')
            yield candidate


def check_listing(manifest):
    """Enforce the submission guide's listing rules the JSON schema leaves open."""
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})
    for key in REQUIRED_TEXT:
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f'interface.{key} must be a nonempty string.')
    for key in LISTING_URLS:
        value = interface.get(key)
        if not isinstance(value, str) or len(value) > MAX_URL:
            raise SystemExit(f'interface.{key} must be a URL of at most {MAX_URL} characters.')
        parts = urlsplit(value)
        if parts.scheme != 'https' or not parts.hostname:
            raise SystemExit(f'interface.{key} must be an https URL with a host.')
        if parts.username is not None or parts.password is not None:
            raise SystemExit(f'interface.{key} must not embed credentials.')


def check_png(data, label):
    """Parse a whole PNG: signature, CRC of every chunk, IHDR first, IEND last, a complete zlib stream."""
    if data[:8] != PNG_SIGNATURE:
        raise SystemExit(f'{label}: not a PNG.')
    offset, chunks, idat = 8, [], b''
    while offset < len(data):
        if offset + 12 > len(data):
            raise SystemExit(f'{label}: truncated chunk.')
        length, kind = struct.unpack('>I4s', data[offset:offset + 8])
        body = data[offset + 8:offset + 8 + length]
        crc_bytes = data[offset + 8 + length:offset + 12 + length]
        if len(body) != length or len(crc_bytes) != 4:
            raise SystemExit(f'{label}: truncated {kind!r} chunk.')
        if zlib.crc32(kind + body) != struct.unpack('>I', crc_bytes)[0]:
            raise SystemExit(f'{label}: bad CRC in {kind!r} chunk.')
        chunks.append(kind)
        if kind == b'IHDR':
            width, height = struct.unpack('>II', body[:8])
        elif kind == b'IDAT':
            idat += body
        offset += 12 + length
    if not chunks or chunks[0] != b'IHDR' or chunks[-1] != b'IEND' or b'IDAT' not in chunks:
        raise SystemExit(f'{label}: missing IHDR, IDAT or IEND.')
    decoder = zlib.decompressobj()
    try:
        decoder.decompress(idat)
    except zlib.error as error:
        raise SystemExit(f'{label}: corrupt image data ({error}).')
    if not decoder.eof:
        raise SystemExit(f'{label}: incomplete image data.')
    if width != height or not 48 <= width <= MAX_ICON_SIDE:
        raise SystemExit(f'{label}: must be square, 48 to {MAX_ICON_SIDE} pixels a side (is {width}x{height}).')
    return width, height


def check_icons(manifest, plugin=PLUGIN):
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})
    for key in ICONS:
        check_png((plugin / interface[key]).read_bytes(), f'interface.{key}')


def check_review(manifest):
    review = manifest.get('extensions', {}).get('com.openai', {}).get('review') or {}
    if review.get('test_cases') is not None:
        raise SystemExit('plugin.json declares review.test_cases; an upload would replace '
                         'or clear the cases saved in the portal draft. Remove them.')


def build(output, plugin=PLUGIN):
    manifest = json.loads((plugin / 'plugin.json').read_text())
    check_review(manifest)
    check_listing(manifest)
    check_icons(manifest, plugin)
    sources = list(files(plugin))
    output = Path(output)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sources:
            info = zipfile.ZipInfo(path.relative_to(plugin).as_posix(), EPOCH)
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes(), zipfile.ZIP_DEFLATED)
    return output


if __name__ == '__main__':
    out = build(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'reason-chatgpt.zip')
    with zipfile.ZipFile(out) as archive:
        print(f'{out}: {len(archive.namelist())} files')
        for name in archive.namelist():
            print('  ' + name)
