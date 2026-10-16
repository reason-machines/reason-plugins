"""Exercise the published package through the actual Codex installer."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MarketplaceInstallation(unittest.TestCase):
    def test_clean_install(self):
        self.install(with_legacy=False)

    def test_install_alongside_retired_marketplace(self):
        self.install(with_legacy=True)

    def install(self, with_legacy):
        if not shutil.which('codex'):
            self.fail('The Codex CLI is required for installation tests')
        with tempfile.TemporaryDirectory(prefix='reason-plugin-test-') as directory:
            temp = Path(directory)
            client = temp / 'client'
            client.mkdir()
            env = dict(os.environ, CODEX_HOME=str(client))

            def codex(*args):
                result = subprocess.run(['codex', 'plugin', *args], env=env,
                                        text=True, capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout

            if with_legacy:
                legacy = temp / 'legacy' / '.agents' / 'plugins'
                legacy.mkdir(parents=True)
                (legacy / 'marketplace.json').write_text(json.dumps({
                    'name': 'ara', 'plugins': []
                }))
                codex('marketplace', 'add', str(temp / 'legacy'))
            codex('marketplace', 'add', str(ROOT))
            codex('add', 'reason@reason')
            listing = codex('list')
            self.assertIn('reason@reason', listing)
            self.assertIn('installed, enabled', listing)
            cached = list((client / 'plugins' / 'cache').rglob('.mcp.json'))
            self.assertEqual(len(cached), 1)
            self.assertEqual(json.loads(cached[0].read_text()), {
                'mcpServers': {'reason': {
                    'type': 'http', 'url': 'https://mcp.reasonmachines.com/mcp'
                }}
            })
            self.assertTrue((cached[0].parent / 'skills/reason/SKILL.md').is_file())
            plugin = json.loads((cached[0].parent / '.codex-plugin/plugin.json').read_text())
            portable = json.loads((cached[0].parent / 'plugin.json').read_text())
            self.assertEqual(portable['$schema'],
                             'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json')
            self.assertEqual(portable['name'], 'reason')
            self.assertEqual(portable['version'], '1.2.0')
            self.assertEqual(portable['version'], plugin['version'])
            interface = portable['extensions']['com.openai']['interface']
            self.assertEqual(interface, plugin['interface'])
            self.assertEqual(interface['displayName'], 'Reason')
            self.assertEqual(interface['shortDescription'], 'Cloud coding across machines')
            self.assertLessEqual(len(interface['shortDescription']), 30)
            for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
                self.assertTrue(interface[key].startswith('https://'), key)
            self.assertEqual(json.loads((cached[0].parent / 'mcp.json').read_text()), {
                '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
                'mcpServers': {'reason': {
                    'type': 'streamable-http', 'url': 'https://mcp.reasonmachines.com/mcp'
                }}
            })
            for key in ['composerIcon', 'logo', 'logoDark']:
                icon = cached[0].parent / plugin['interface'][key]
                self.assertEqual(icon.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
            self.assertTrue((cached[0].parent / 'skills/reason/agents/openai.yaml').is_file())

            for path in ['.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json']:
                manifest = json.loads((ROOT / path).read_text())
                self.assertEqual(manifest['name'], 'reason')
                self.assertEqual([p['name'] for p in manifest['plugins']], ['reason'])
            self.assertEqual(sorted(p.name for p in (ROOT / 'plugins').iterdir()), ['reason'])


RETIRED_SERVER = '/mcp/ara'
SERVER_URL = 'https://mcp.reasonmachines.com/mcp'
RAW_MAIN = 'https://raw.githubusercontent.com/reason-machines/reason-plugins/main/'


class PublishedManifests(unittest.TestCase):
    def test_former_claude_plugin_names_move_to_reason(self):
        # Claude Code follows `renames` for people who enabled a plugin under a
        # name this marketplace no longer lists. Without an entry their install
        # fails with "Plugin ara not found in marketplace ara".
        manifest = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        listed = {plugin['name'] for plugin in manifest['plugins']}
        self.assertEqual(manifest['renames'], {'ara-handoff': 'reason', 'ara': 'reason'})
        for former, current in manifest['renames'].items():
            self.assertNotIn(former, listed)
            self.assertIn(current, listed)

    def test_nothing_installable_points_at_the_retired_server(self):
        # README.md names the retired address to tell people to remove it.
        checked = 0
        for path in ROOT.rglob('*'):
            relative = path.relative_to(ROOT)
            if not path.is_file() or relative.parts[0] in {'.git', 'tests'} or relative.name == 'README.md':
                continue
            if path.suffix in {'.json', '.yaml', '.yml', '.toml', '.md'}:
                checked += 1
                self.assertNotIn(RETIRED_SERVER, path.read_text(), str(relative))
        self.assertGreater(checked, 5)

    def test_registry_entry_is_the_server_the_plugin_installs(self):
        server = json.loads((ROOT / 'server.json').read_text())
        plugin = json.loads((ROOT / 'plugins/reason/.mcp.json').read_text())
        self.assertEqual(plugin['mcpServers']['reason']['url'], SERVER_URL)
        self.assertEqual(server['remotes'], [{'type': 'streamable-http', 'url': SERVER_URL}])
        # The publish workflow signs in with GitHub OIDC, which grants only
        # names under this organization.
        self.assertRegex(server['name'], r'^io\.github\.reason-machines/[a-zA-Z0-9._-]+$')
        self.assertLessEqual(len(server['description']), 100)
        self.assertLessEqual(len(server['title']), 100)
        for icon in server['icons']:
            self.assertTrue(icon['src'].startswith(RAW_MAIN), icon['src'])
            image = ROOT / icon['src'][len(RAW_MAIN):]
            self.assertEqual(image.read_bytes()[:8], b'\x89PNG\r\n\x1a\n', icon['src'])


if __name__ == '__main__':
    unittest.main()
