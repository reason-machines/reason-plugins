"""Check the Cursor Marketplace package (also what Grok Bot installs).

Mirrors the submission checklist in https://cursor.com/docs/reference/plugins.md
and the checks in cursor/plugin-template's scripts/validate-template.mjs.
"""
import json
from pathlib import Path
import posixpath
import re
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
SERVER_URL = 'https://mcp.reasonmachines.com/mcp'
PLUGIN_NAME = re.compile(r'^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$')
MARKETPLACE_NAME = re.compile(r'^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$')
KEBAB = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
PLACEHOLDER = re.compile(r'\$\{([^}]+)\}')
PATH_FIELDS = ['logo', 'rules', 'skills', 'agents', 'commands', 'hooks', 'mcpServers']
COMPONENTS = {  # directory: (extensions, required frontmatter keys)
    'rules': ({'.md', '.mdc', '.markdown'}, ['description']),
    'agents': ({'.md', '.mdc', '.markdown'}, ['name', 'description']),
    'commands': ({'.md', '.mdc', '.markdown', '.txt'}, ['name', 'description']),
}


def frontmatter(path):
    text = path.read_text().replace('\r\n', '\n')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        return None
    block = text[4:text.index('\n---\n', 4)]
    fields = {}
    for line in block.split('\n'):
        if ':' in line and not line.startswith((' ', '#')):
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip()
    return fields


def path_values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [p for item in value for p in path_values(item)]
    if isinstance(value, dict):
        return [value[k] for k in ('path', 'file') if isinstance(value.get(k), str)]
    return []


def safe_relative(value):
    if value.startswith(('http://', 'https://')):
        return True
    if value.startswith('/') or re.match(r'^[A-Za-z]:', value):
        return False
    normalized = posixpath.normpath(value.replace('\\', '/'))
    return normalized != '..' and not normalized.startswith('../') and '/../' not in value


class CursorMarketplace(unittest.TestCase):
    def setUp(self):
        self.marketplace = json.loads((ROOT / '.cursor-plugin/marketplace.json').read_text())

    def plugins(self):
        for entry in self.marketplace['plugins']:
            directory = ROOT / entry['source']
            yield entry, directory, json.loads((directory / '.cursor-plugin/plugin.json').read_text())

    def test_marketplace_manifest(self):
        self.assertRegex(self.marketplace['name'], MARKETPLACE_NAME)
        self.assertTrue(self.marketplace['owner']['name'])
        names = [entry['name'] for entry in self.marketplace['plugins']]
        self.assertEqual(names, ['reason'])
        self.assertEqual(len(names), len(set(names)))
        # A root plugin.json would make this repository a single-plugin
        # package as well; keep one layout.
        self.assertFalse((ROOT / '.cursor-plugin/plugin.json').exists())

    def test_plugin_manifests(self):
        for entry, directory, plugin in self.plugins():
            self.assertTrue(safe_relative(entry['source']), entry['source'])
            self.assertTrue(directory.is_dir())
            self.assertRegex(plugin['name'], PLUGIN_NAME)
            self.assertRegex(plugin['name'], KEBAB)
            self.assertEqual(plugin['name'], entry['name'])
            self.assertTrue(plugin['description'])
            self.assertRegex(plugin['version'], r'^\d+\.\d+\.\d+$')
            for field in PATH_FIELDS:
                for value in path_values(plugin.get(field)):
                    self.assertFalse(value.startswith(('http://', 'https://')),
                                     f'{field} should be committed and relative')
                    self.assertTrue(safe_relative(value), f'{field}: {value}')
                    self.assertTrue((directory / value).exists(), f'{field}: {value} is missing')

    def test_versions_agree(self):
        for _, directory, plugin in self.plugins():
            for other in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'plugin.json']:
                self.assertEqual(json.loads((directory / other).read_text())['version'],
                                 plugin['version'], other)
            self.assertEqual(self.marketplace['metadata']['version'], plugin['version'])

    def test_logo_is_square_with_a_background_plate(self):
        for _, directory, plugin in self.plugins():
            data = (directory / plugin['logo']).read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
            width, height, _, color_type = struct.unpack('>IIBB', data[16:26])
            self.assertEqual(width, height)
            self.assertGreaterEqual(width, 256)
            # Colour types 4 and 6 carry alpha; an opaque logo keeps its plate
            # on light and dark listings.
            self.assertIn(color_type, (0, 2, 3))

    def test_mcp_server_is_oauth_only(self):
        for _, directory, plugin in self.plugins():
            config = json.loads((directory / plugin['mcpServers']).read_text())
            self.assertEqual(config, {'mcpServers': {'reason': {'url': SERVER_URL}}})

    def test_every_placeholder_is_declared(self):
        for _, directory, plugin in self.plugins():
            declared = set(plugin.get('variables', {}).get('properties', {}))
            for value in path_values(plugin.get('mcpServers')) + path_values(plugin.get('hooks')):
                used = set(PLACEHOLDER.findall((directory / value).read_text()))
                used -= {'CURSOR_PLUGIN_ROOT', 'CLAUDE_PLUGIN_ROOT'}
                self.assertLessEqual(used, declared, value)

    def test_component_frontmatter(self):
        for _, directory, plugin in self.plugins():
            skills = list((directory / 'skills').rglob('SKILL.md'))
            self.assertTrue(skills)
            names = []
            for skill in skills:
                fields = frontmatter(skill)
                self.assertIsNotNone(fields, skill)
                self.assertRegex(fields.get('name', ''), KEBAB, skill)
                self.assertEqual(fields['name'], skill.parent.name)
                self.assertTrue(fields.get('description'), skill)
                self.assertLessEqual(len(fields['description']), 1024, skill)
                names.append(fields['name'])
            for folder, (extensions, keys) in COMPONENTS.items():
                for path in (directory / folder).rglob('*') if (directory / folder).is_dir() else []:
                    if path.suffix not in extensions:
                        continue
                    fields = frontmatter(path)
                    self.assertIsNotNone(fields, path)
                    for key in keys:
                        self.assertTrue(fields.get(key), f'{path}: {key}')
                    if 'name' in keys:
                        self.assertRegex(fields['name'], KEBAB, path)
                        self.assertEqual(fields['name'], path.stem, path)
                        names.append(fields['name'])
            self.assertEqual(len(names), len(set(names)), names)

    def test_skill_names_real_tools(self):
        # Tool names the skill teaches, as the server lists them.
        text = (ROOT / 'plugins/reason/skills/reason/SKILL.md').read_text()
        for tool in ['getSelf', 'listRepositories', 'createSession', 'getSession',
                     'sendSessionMessage', 'listSessionMessages', 'listSessionConversation',
                     'listSessionEvents', 'cancelSession', 'retrySession', 'forkSession',
                     'triggerPrReview', 'createAutomation', 'createAutomationTrigger',
                     'listDevices', 'listMachines']:
            self.assertIn(f'`{tool}', text, tool)
        # Retired Projects tools are no longer served.
        for retired in ['listProjects', 'updateProject', 'getProject']:
            self.assertNotIn(retired, text)


class OtherManifestsStillParse(unittest.TestCase):
    def test_json_files_parse(self):
        files = [p for p in ROOT.rglob('*.json') if '.git' not in p.parts]
        self.assertGreater(len(files), 8)
        for path in files:
            if path.stat().st_size:
                json.loads(path.read_text())


if __name__ == '__main__':
    unittest.main()
