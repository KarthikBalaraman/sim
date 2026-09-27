#!/usr/bin/env python3
"""
test_simulator.py — Automated Consistency and Invariant Verification Suite

Designed for both AI agents and human developers to verify the integrity
of the Court Booking Revenue Simulator in < 1 second with ZERO external dependencies.

Run:
    python test_simulator.py
    python -m unittest tests/test_simulator.py
"""

import unittest
import os
import sys
import ast
import json
import re
import hmac
import hashlib
import base64
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) if os.path.basename(CURRENT_DIR) == 'tests' else CURRENT_DIR

# Ensure server module is importable
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'server'))
sys.path.insert(0, PROJECT_ROOT)

def find_file(rel_path, subdirs=None):
    candidates = []
    if subdirs:
        for s in subdirs:
            candidates.append(os.path.join(PROJECT_ROOT, s, rel_path))
    candidates.append(os.path.join(PROJECT_ROOT, rel_path))
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


class TestZeroDependencies(unittest.TestCase):
    """Ensures server.py strictly adheres to the standard-library-only rule."""

    def test_no_third_party_imports_in_server(self):
        server_path = find_file('server.py', ['server'])
        self.assertTrue(os.path.exists(server_path), f"server.py must exist at {server_path}")

        with open(server_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename='server.py')

        allowed_stdlib = {
            'os', 'sys', 'json', 'hmac', 'hashlib', 'base64', 'time',
            'urllib', 'http', 'typing', 'ast', 'unittest', 're'
        }

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.add(node.module.split('.')[0])

        disallowed = imported_modules - allowed_stdlib
        self.assertEqual(
            disallowed, set(),
            f"server.py must NOT import third-party packages! Disallowed found: {disallowed}"
        )


class TestConfigJsonSchema(unittest.TestCase):
    """Validates structure, types, and constraints in config.json."""

    def setUp(self):
        self.config_path = find_file('config.json', ['config'])
        self.assertTrue(os.path.exists(self.config_path), f"config.json must exist at {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def test_required_currencies_exist(self):
        currencies = self.config.get("currencies", {})
        self.assertIn("INR", currencies, "config.json currencies must contain INR settings")
        self.assertIn("AED", currencies, "config.json currencies must contain AED settings")

    def test_currency_sections_and_invariants(self):
        currencies = self.config.get("currencies", {})
        for code, conf in currencies.items():
            self.assertIn("symbol", conf)
            if code == "INR":
                self.assertEqual(conf["symbol"], "₹", "INR symbol must be ₹ without space")
            elif code == "AED":
                self.assertEqual(conf["symbol"], "AED ", "AED symbol must include trailing space")

            # Pipeline section
            self.assertIn("pipeline", conf)
            p = conf["pipeline"]
            self.assertGreater(p.get("courtsPerVenue", 0), 0)
            self.assertGreaterEqual(p.get("startingVenues", -1), 0)
            self.assertGreaterEqual(p.get("venueGrowth", -1), 0)
            self.assertGreater(p.get("liaisonCount", 0), 0)

            # Model A section
            self.assertIn("modelA", conf)
            mA = conf["modelA"]
            self.assertGreater(mA.get("baseRate", 0), 0)
            self.assertGreaterEqual(mA.get("grossCommission", 0), 0)
            self.assertGreaterEqual(mA.get("gatewayFee", 0), 0)

            # Model B section
            self.assertIn("modelB", conf)
            mB = conf["modelB"]
            self.assertGreaterEqual(mB.get("subscriptionCost", 0), 0)
            self.assertLessEqual(mB.get("subscriptionMin", 0), mB.get("subscriptionMax", 10000))

            # Model C section
            self.assertIn("modelC", conf)
            mC = conf["modelC"]
            self.assertGreaterEqual(mC.get("bookingFee", 0), 0)
            self.assertLessEqual(mC.get("bookingFeeMin", 0), mC.get("bookingFeeMax", 1000))


class TestSimulatorHtmlIntegrity(unittest.TestCase):
    """Verifies that Simulator.html has all required DOM elements and structural patterns."""

    def setUp(self):
        self.html_path = find_file('Simulator.html', ['client'])
        self.assertTrue(os.path.exists(self.html_path), f"Simulator.html must exist at {self.html_path}")
        with open(self.html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

    def test_critical_dom_element_ids_exist(self):
        required_ids = [
            'currencySelect',
            'courtsPerVenue',
            'startingVenues',
            'venueGrowth',
            'liaisonCount',
            'baseRate',
            'hoursPerWeek',
            'grossCommission',
            'subCost',
            'subCostInput',
            'bookingFee',
            'licenseeShare',
            'subLicenseeShare',
            'bookingLicenseeShare',
            'syncSplit',
            'horizonStart',
            'horizonEnd'
        ]
        for elem_id in required_ids:
            pattern = rf'id=["\']?{re.escape(elem_id)}["\']?'
            self.assertRegex(
                self.html, pattern,
                f"Simulator.html is missing required DOM element id='{elem_id}'"
            )

    def test_flex_input_prefix_pattern(self):
        """Ensures currency symbols in inputs use flexbox input-prefix rather than absolute overlay."""
        self.assertIn('input-prefix', self.html, "Simulator.html must use input-prefix class for input badges")
        self.assertRegex(
            self.html,
            r'class="[^"]*currency-symbol[^"]*input-prefix[^"]*"',
            "Currency symbol spans inside inputs must have .input-prefix"
        )

    def test_zero_falsy_protection_in_calculate(self):
        """Ensures calculate() does not use falsy fallback (||) for numerical inputs."""
        self.assertNotRegex(
            self.html,
            r'parseInt\(document\.getElementById\([\'"]startingVenues[\'"]\)\.value\)\s*\|\|',
            "startingVenues input reading must protect against zero-falsy bug (use isNaN)"
        )


class TestServerSecurityLogic(unittest.TestCase):
    """Verifies HMAC session signing and authorization logic."""

    def test_token_creation_and_verification(self):
        import server.server as server
        user_info = {
            'email': 'developer@example.com',
            'name': 'Dev Tester',
            'picture': ''
        }
        server.ALLOWED_USERS.add('developer@example.com')

        token = server.create_session_token(user_info)
        self.assertIsInstance(token, str)
        self.assertIn('.', token)

        payload = server.verify_session_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['email'], 'developer@example.com')

        b64_part, _ = token.split('.', 1)
        bad_token = f"{b64_part}.invalid_signature"
        self.assertIsNone(server.verify_session_token(bad_token))

        unauthorized_token = server.create_session_token({'email': 'intruder@forbidden.com'})
        self.assertIsNone(server.verify_session_token(unauthorized_token))

    def test_domain_authorization(self):
        import server.server as server
        server.ALLOWED_DOMAINS = {'company.com'}
        self.assertTrue(server.is_email_authorized('alice@company.com'))
        self.assertTrue(server.is_email_authorized('bob@sub.company.com') or server.is_email_authorized('bob@company.com'))
        self.assertFalse(server.is_email_authorized('hacker@other.com'))


class TestAgentDocumentationSync(unittest.TestCase):
    """Ensures all agent guide files exist and contain explicit synchronization rules."""

    def test_agent_files_exist_and_contain_sync_instructions(self):
        agent_files = {
            'AGENTS.md': 'Mandatory Agent & Documentation Synchronization',
            'GEMINI.md': 'Mandatory Agent & Documentation Synchronization',
            'CLAUDE.md': 'Mandatory Documentation & Agent Sync',
            '.cursorrules': 'Mandatory Documentation & Agent Sync',
            '.github/copilot-instructions.md': 'Mandatory Documentation Synchronization',
            '.agents/rules/simulator-invariants.md': 'Mandatory Agent & Documentation Synchronization',
            'README.md': 'AI Agent Guidelines & Synchronization'
        }

        for rel_path, sync_phrase in agent_files.items():
            full_path = os.path.join(PROJECT_ROOT, rel_path.replace('/', os.sep))
            self.assertTrue(os.path.exists(full_path), f"Agent instruction file missing: {rel_path}")
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn(
                sync_phrase, content,
                f"{rel_path} must contain explicit instructions to update agent files on change ('{sync_phrase}')"
            )


class TestRailwayDeploymentConfig(unittest.TestCase):
    """Verifies existence and correctness of Railway and container deployment configuration."""

    def test_railway_files_exist(self):
        required_files = [
            'Dockerfile',
            '.dockerignore',
            'railway.json',
            'Procfile',
            'nixpacks.toml'
        ]
        for fname in required_files:
            fpath = os.path.join(PROJECT_ROOT, fname)
            self.assertTrue(os.path.exists(fpath), f"Railway deployment file missing: {fname}")

    def test_railway_json_schema(self):
        fpath = os.path.join(PROJECT_ROOT, 'railway.json')
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('deploy', data)
        self.assertEqual(data['deploy'].get('healthcheckPath'), '/api/health')

    def test_dockerfile_contents(self):
        fpath = os.path.join(PROJECT_ROOT, 'Dockerfile')
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('python:3.12-slim', content)
        self.assertIn('server/server.py', content)

    def test_dockerignore_protects_env(self):
        fpath = os.path.join(PROJECT_ROOT, '.dockerignore')
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('.env', content)


if __name__ == '__main__':
    unittest.main()
