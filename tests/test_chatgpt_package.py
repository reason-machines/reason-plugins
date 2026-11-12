"""Check the ChatGPT/Codex plugin directory ZIP.

Validates the portable manifests against the vendored Agent Plugins 1.0.0
schemas (tests/schemas, copied from https://agent-plugins.org/schemas/1.0.0/)
and the public-submission limits in
https://developers.openai.com/plugins/deploy/submission.md.
"""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/reason'
SCHEMAS = Path(__file__).resolve().parent / 'schemas'
SERVER_URL = 'https://mcp.reasonmachines.com/mcp'

spec = importlib.util.spec_from_file_location('build_chatgpt_zip', ROOT / 'scripts/build_chatgpt_zip.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def png(width, height):
    """A minimal valid 8-bit greyscale PNG of the given size."""
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    rows = zlib.compress(b'\x00' * ((width + 1) * height), 9)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 0, 0, 0, 0))
            + chunk(b'IDAT', rows) + chunk(b'IEND', b''))


def validate(instance, schema, root=None, where='$'):
    """Return schema errors for the JSON Schema keywords the Agent Plugins schemas use."""
    root = root or schema
    if '$ref' in schema:
        target = root
        for part in schema['$ref'].lstrip('#/').split('/'):
            target = target[part]
        return validate(instance, target, root, where)
    errors = []
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool}
    if 'type' in schema and not isinstance(instance, types[schema['type']]):
        return [f'{where}: expected {schema["type"]}']
    if 'const' in schema and instance != schema['const']:
        errors.append(f'{where}: expected {schema["const"]!r}')
    if 'enum' in schema and instance not in schema['enum']:
        errors.append(f'{where}: not one of {schema["enum"]}')
    if isinstance(instance, str):
        if len(instance) < schema.get('minLength', 0):
            errors.append(f'{where}: too short')
        if 'maxLength' in schema and len(instance) > schema['maxLength']:
            errors.append(f'{where}: too long')
        if 'pattern' in schema and not re.search(schema['pattern'], instance):
            errors.append(f'{where}: does not match {schema["pattern"]}')
    if isinstance(instance, list) and 'items' in schema:
        for i, item in enumerate(instance):
            errors += validate(item, schema['items'], root, f'{where}[{i}]')
    if isinstance(instance, dict):
        for key in schema.get('required', []):
            if key not in instance:
                errors.append(f'{where}: missing {key}')
        props = schema.get('properties', {})
        for key, value in instance.items():
            if 'propertyNames' in schema:
                errors += validate(key, schema['propertyNames'], root, f'{where}.{key} (name)')
            if key in props:
                errors += validate(value, props[key], root, f'{where}.{key}')
            elif schema.get('additionalProperties') is False:
                errors.append(f'{where}: unexpected {key}')
            elif isinstance(schema.get('additionalProperties'), dict):
                errors += validate(value, schema['additionalProperties'], root, f'{where}.{key}')
    if 'not' in schema and not validate(instance, schema['not'], root, where):
        errors.append(f'{where}: matches a forbidden schema')
    if 'oneOf' in schema:
        matches = sum(1 for option in schema['oneOf'] if not validate(instance, option, root, where))
        if matches != 1:
            errors.append(f'{where}: matches {matches} of oneOf')
    return errors


class ChatGPTPackage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.zip_path = builder.build(Path(self.tmp.name) / 'reason-chatgpt.zip')
        self.archive = zipfile.ZipFile(self.zip_path)
        self.names = self.archive.namelist()
        self.manifest = json.loads(self.archive.read('plugin.json'))
        self.openai = self.manifest['extensions']['com.openai']
        self.interface = self.openai['interface']

    def tearDown(self):
        self.archive.close()
        self.tmp.cleanup()

    def test_zip_holds_only_the_portable_package(self):
        top = {name.split('/')[0] for name in self.names}
        self.assertEqual(top, {'plugin.json', 'mcp.json', 'skills', 'assets'})
        self.assertIn('skills/reason/SKILL.md', self.names)
        for name in self.names:
            self.assertFalse(name.endswith(('.app.json', 'hooks.json')), name)
            self.assertNotIn('..', name.split('/'))

    def test_manifests_match_the_agent_plugins_schemas(self):
        plugin_schema = json.loads((SCHEMAS / 'agent-plugins-1.0.0-plugin.schema.json').read_text())
        mcp_schema = json.loads((SCHEMAS / 'agent-plugins-1.0.0-mcp.schema.json').read_text())
        self.assertEqual(validate(self.manifest, plugin_schema), [])
        mcp = json.loads(self.archive.read('mcp.json'))
        self.assertEqual(validate(mcp, mcp_schema), [])
        # Exactly one remote server, no headers: authentication comes from OAuth discovery.
        self.assertEqual(mcp['mcpServers'], {'reason': {'type': 'streamable-http', 'url': SERVER_URL}})

    def test_validator_rejects_a_bad_manifest(self):
        schema = json.loads((SCHEMAS / 'agent-plugins-1.0.0-plugin.schema.json').read_text())
        self.assertTrue(validate({'name': 'Reason'}, schema))
        self.assertTrue(validate({**self.manifest, 'apps': './.app.json'}, schema))

    def test_listing_meets_submission_limits(self):
        self.assertEqual(self.manifest['name'], 'reason')
        self.assertRegex(self.manifest['version'], r'^\d+\.\d+\.\d+$')
        self.assertEqual(self.interface['displayName'], 'Reason')
        self.assertLessEqual(len(self.interface['displayName']), 30)
        self.assertLessEqual(len(self.interface['shortDescription']), 30)
        self.assertLessEqual(len(self.interface['longDescription']), 4000)
        self.assertLessEqual(len(self.interface['developerName']), 80)
        self.assertTrue(self.interface['category'])
        prompts = self.interface['defaultPrompt']
        self.assertLessEqual(len(prompts), 3)
        self.assertEqual(len(prompts), len(set(prompts)))
        for prompt in prompts:
            self.assertLessEqual(len(prompt), 128)
        for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
            self.assertTrue(self.interface[key].startswith('https://'), key)
        self.assertTrue(self.interface['privacyPolicyURL'].endswith('/privacy-policy'))
        self.assertTrue(self.interface['termsOfServiceURL'].endswith('/terms-of-service'))
        text = ' '.join([self.interface['shortDescription'], self.interface['longDescription'], *prompts])
        # Guidelines: no pricing or upsell copy, no "MCP"/"Plugin" suffix on the name.
        self.assertNotRegex(text.lower(), r'\b(price|pricing|free trial|discount|subscribe|upgrade)\b')
        self.assertNotRegex(self.interface['displayName'], r'(?i)\b(mcp|plugin)\b')
        self.assertNotRegex(text.lower(), r'\bprojects?\b')

    def test_icons_are_square_pngs_in_the_zip(self):
        for key in ['composerIcon', 'logo', 'logoDark']:
            name = self.interface[key].removeprefix('./')
            self.assertIn(name, self.names, key)
            data = self.archive.read(name)
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n', key)
            width, height = struct.unpack('>II', data[16:24])
            self.assertEqual(width, height, key)
            self.assertGreaterEqual(width, 48, key)
            self.assertLessEqual(len(data), 5 * 1024 * 1024, key)

    def test_no_credentials_or_reviewer_fields(self):
        review = self.openai.get('review', {})
        for key in ['test_credentials', 'reviewer_instructions']:
            self.assertNotIn(key, review)
        for name in self.names:
            data = self.archive.read(name)
            if name.endswith(('.json', '.md', '.yaml')):
                self.assertNotRegex(data.decode(), r'(?i)(bearer\s+[a-z0-9_\-]{20,}|password\s*[:=])', name)

    def test_build_refuses_bad_listing_metadata(self):
        builder.check_listing(self.manifest)
        bad = {
            'websiteURL': 'https://user:secret@reasonmachines.com',
            'supportURL': 'https://reasonmachines.com/' + 'a' * 1024,
            'privacyPolicyURL': 'http://reasonmachines.com/privacy-policy',
            'termsOfServiceURL': 'https:///terms-of-service',
            'longDescription': '   ',
            'shortDescription': '',
        }
        for value in ['https://exa mple.com', 'https://reasonmachines.com/ x',
                      'https://reasonmachines.com\n', 'https://reasonmachines.com:invalid',
                      'https://reasonmachines.com:99999', 'https://[::1/',
                      'https://reasonmachines.com:0', 'https://reason\u200bmachines.com',
                      'https://reasonmachines.com/\u200d', 'https://reasonmachines.com/\ufeff',
                      'https://reasonmachines.com/\u2060x', 'https://reasonmachines.com/\u00ad']:
            manifest = json.loads(json.dumps(self.manifest))
            manifest['extensions']['com.openai']['interface']['supportURL'] = value
            with self.assertRaises(SystemExit, msg=value):
                builder.check_listing(manifest)
        for key, value in bad.items():
            manifest = json.loads(json.dumps(self.manifest))
            manifest['extensions']['com.openai']['interface'][key] = value
            with self.assertRaises(SystemExit, msg=key):
                builder.check_listing(manifest)

    def test_build_refuses_corrupt_or_oversized_icons(self):
        good = self.archive.read('assets/reason-logo.png')
        self.assertEqual(builder.check_png(good, 'logo'), (512, 512))
        builder.check_png(png(4096, 4096), 'largest')
        for label, data in {
            'truncated header': good[:24],
            'truncated data': good[:len(good) // 2],
            'bad crc': good[:40] + bytes([good[40] ^ 0xFF]) + good[41:],
            'too large': png(8192, 8192),
            'too small': png(16, 16),
            'not square': png(512, 256),
        }.items():
            with self.assertRaises(SystemExit, msg=label):
                builder.check_png(data, label)

    def test_build_refuses_png_without_raster_data(self):
        def chunk(kind, body):
            return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
        header = chunk(b'IHDR', struct.pack('>IIBBBBB', 48, 48, 8, 2, 0, 0, 0))
        for raster in [b'', b'\x00', b'\x05' + b'\x00' * (48 * 3), b'\x00' * (48 * 145 + 1)]:
            data = (builder.PNG_SIGNATURE + header + chunk(b'IDAT', zlib.compress(raster))
                    + chunk(b'IEND', b''))
            with self.assertRaises(SystemExit):
                builder.check_png(data, 'invalid raster')

    def test_build_refuses_invalid_png_structure(self):
        def chunk(kind, body):
            return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
        header = chunk(b'IHDR', struct.pack('>IIBBBBB', 48, 48, 8, 0, 0, 0, 0))
        compressed = zlib.compress(b'\x00' * (49 * 48))
        idat, end = chunk(b'IDAT', compressed), chunk(b'IEND', b'')
        for body in [header + header + idat + end,
                     header + idat + chunk(b'tEXt', b'key\x00value') + idat + end,
                     chunk(b'IHDR', b'123') + idat + end,
                     chunk(b'IHDR', struct.pack('>IIBBBBB', 48, 48, 3, 7, 0, 0, 0)) + idat + end,
                     header + chunk(b'IDAT', compressed + b'extra') + end,
                     header + idat + end + b'extra']:
            with self.assertRaises(SystemExit):
                builder.check_png(builder.PNG_SIGNATURE + body, 'invalid structure')

    def test_build_refuses_palette_png_without_plte(self):
        def chunk(kind, body):
            return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
        header = chunk(b'IHDR', struct.pack('>IIBBBBB', 48, 48, 8, 3, 0, 0, 0))
        idat, end = chunk(b'IDAT', zlib.compress(b'\x00' * (49 * 48))), chunk(b'IEND', b'')
        palette = chunk(b'PLTE', b'\x00\x00\x00')
        builder.check_png(builder.PNG_SIGNATURE + header + palette + idat + end, 'palette')
        for body in [header + idat + end, header + idat + palette + end]:
            with self.assertRaises(SystemExit):
                builder.check_png(builder.PNG_SIGNATURE + body, 'palette without PLTE')

    def test_build_refuses_icons_not_in_the_package(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'reason'
            shutil.copytree(PLUGIN, copy)
            outside = Path(directory) / 'outside.png'
            outside.write_bytes(self.archive.read('assets/reason-logo.png'))
            for value in [str(outside), '../outside.png', 'unpackaged.png']:
                (copy / 'unpackaged.png').write_bytes(outside.read_bytes())
                manifest = json.loads(json.dumps(self.manifest))
                manifest['extensions']['com.openai']['interface']['logo'] = value
                with self.assertRaises(SystemExit):
                    builder.check_icons(manifest, copy)

    def test_build_refuses_symlinks_out_of_the_package(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'reason'
            shutil.copytree(PLUGIN, copy)
            outside = Path(directory) / 'outside.txt'
            outside.write_text('not part of the package')
            (copy / 'assets/external.txt').symlink_to(outside)
            with self.assertRaises(SystemExit):
                builder.build(Path(directory) / 'out.zip', copy)
            (copy / 'assets/external.txt').unlink()
            builder.build(Path(directory) / 'out.zip', copy)

    def test_upload_keeps_the_drafts_review_cases(self):
        # The portal draft's review cases are managed by its earlier ZIP. A
        # package that omits test_cases preserves them; one that declares them
        # replaces all eight, so add them only from the draft's canonical text.
        self.assertNotIn('test_cases', self.openai.get('review', {}))
        source = json.loads((PLUGIN / 'plugin.json').read_text())
        self.assertNotIn('test_cases', source['extensions']['com.openai'].get('review', {}))
        # `test_cases: {}` clears both lists in the portal; the build must refuse it.
        for declared in [{}, {'positive': [], 'negative': []}]:
            manifest = {'extensions': {'com.openai': {'review': {'test_cases': declared}}}}
            with self.assertRaises(SystemExit):
                builder.check_review(manifest)
        builder.check_review({'extensions': {'com.openai': {'review': {'test_cases': None}}}})
        for value in ['invalid', [], False, 42]:
            with self.assertRaises(SystemExit):
                builder.check_review({'extensions': {'com.openai': {'review': value}}})

    def test_missing_pillow_exits_with_install_command(self):
        probe = ("import runpy, sys; sys.modules['PIL'] = None; "
                 f"runpy.run_path({str(ROOT / 'scripts/build_chatgpt_zip.py')!r}, run_name='__main__')")
        result = subprocess.run([sys.executable, '-c', probe], cwd=ROOT,
                                text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr.strip(),
                         'Pillow is required: python3 -m pip install -r scripts/requirements.txt')
        self.assertNotIn('Traceback', result.stderr)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            again = builder.build(Path(directory) / 'again.zip')
            self.assertEqual(again.read_bytes(), self.zip_path.read_bytes())


if __name__ == '__main__':
    unittest.main()
