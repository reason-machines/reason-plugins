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

Install: python3 -m pip install -r scripts/requirements.txt
Usage: python3 scripts/build_chatgpt_zip.py [output.zip]
"""
from io import BytesIO
import json
from pathlib import Path
import struct
import sys
import unicodedata
from urllib.parse import urlsplit
import zipfile
import zlib

try:
    from PIL import Image
except ImportError:
    raise SystemExit('Pillow is required: python3 -m pip install -r scripts/requirements.txt') from None

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
        # Cc control, Cf format (zero-width, BOM, soft hyphen), Z* separators.
        if any(character.isspace() or unicodedata.category(character)[0] in 'CZ' for character in value):
            raise SystemExit(f'interface.{key} must not contain whitespace, control or invisible characters.')
        try:
            parts = urlsplit(value)
            port = parts.port
            if parts.scheme != 'https' or not parts.hostname:
                raise ValueError('expected an https URL with a host')
            if port == 0:
                raise ValueError('port 0 is not a usable port')
            if parts.username is not None or parts.password is not None:
                raise ValueError('embedded credentials are not allowed')
        except ValueError as error:
            raise SystemExit(f'interface.{key}: invalid listing URL ({error}).') from error


def check_png(data, label):
    """Verify PNG integrity and decode its pixels, within the listing's size limit."""
    try:
        with Image.open(BytesIO(data)) as image:
            if image.format != 'PNG':
                raise SystemExit(f'{label}: not a PNG.')
            width, height = image.size
            if width != height or not 48 <= width <= MAX_ICON_SIDE:
                raise SystemExit(f'{label}: must be square, 48 to {MAX_ICON_SIDE} pixels a side (is {width}x{height}).')
            image.verify()
        check_png_stream(data, width, height, label)
        # verify() checks chunks; load() also rejects missing or invalid raster data.
        with Image.open(BytesIO(data)) as image:
            image.load()
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as error:
        raise SystemExit(f'{label}: invalid PNG ({error}).') from error
    return width, height


def check_png_stream(data, width, height, label):
    """Reject structural and raster-length errors that tolerant PNG decoders allow."""
    offset, kinds, compressed = 8, [], []
    while offset < len(data):
        if offset + 12 > len(data):
            raise SystemExit(f'{label}: truncated PNG chunk.')
        length, kind = struct.unpack_from('>I4s', data, offset)
        end = offset + length + 12
        if end > len(data):
            raise SystemExit(f'{label}: truncated PNG chunk.')
        body = data[offset + 8:end - 4]
        if kind == b'IHDR':
            if kinds or length != 13:
                raise SystemExit(f'{label}: expected one 13-byte IHDR first.')
            _, _, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', body)
            depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
            if depth not in depths.get(color, ()) or compression != 0 or filtering != 0 or interlace not in (0, 1):
                raise SystemExit(f'{label}: invalid IHDR fields.')
        elif kind == b'PLTE' and b'IDAT' in kinds:
            raise SystemExit(f'{label}: PLTE must come before IDAT.')
        elif kind == b'IDAT':
            if compressed and kinds[-1] != b'IDAT':
                raise SystemExit(f'{label}: IDAT chunks must be contiguous.')
            compressed.append(body)
        elif kind == b'IEND' and (length != 0 or end != len(data)):
            raise SystemExit(f'{label}: invalid IEND or trailing PNG data.')
        kinds.append(kind)
        offset = end
    if not kinds or kinds[0] != b'IHDR' or kinds[-1] != b'IEND' or not compressed:
        raise SystemExit(f'{label}: incomplete PNG structure.')
    if color == 3 and b'PLTE' not in kinds:
        raise SystemExit(f'{label}: palette PNG has no PLTE chunk.')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    passes = [(0, 0, 1, 1)] if interlace == 0 else [
        (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
        (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
    expected = 0
    for x, y, dx, dy in passes:
        columns, rows = max(0, (width - x + dx - 1) // dx), max(0, (height - y + dy - 1) // dy)
        if columns and rows:
            expected += rows * (1 + (columns * channels * depth + 7) // 8)
    decoder = zlib.decompressobj()
    try:
        raster = decoder.decompress(b''.join(compressed), expected + 1)
    except zlib.error as error:
        raise SystemExit(f'{label}: invalid PNG raster ({error}).') from error
    if len(raster) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise SystemExit(f'{label}: PNG raster length does not match its header.')


def check_icons(manifest, plugin=PLUGIN):
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})
    packaged = set(files(plugin))
    for key in ICONS:
        value = interface.get(key)
        if not isinstance(value, str) or Path(value).is_absolute() or '..' in Path(value).parts:
            raise SystemExit(f'interface.{key}: expected a package-relative icon path.')
        path = plugin / value
        if path not in packaged or plugin.resolve() not in path.resolve().parents:
            raise SystemExit(f'interface.{key}: icon must be included in the package.')
        check_png(path.read_bytes(), f'interface.{key}')


def check_review(manifest):
    review = manifest.get('extensions', {}).get('com.openai', {}).get('review')
    if review is None:
        return
    if not isinstance(review, dict):
        raise SystemExit('com.openai.review must be an object or null.')
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
