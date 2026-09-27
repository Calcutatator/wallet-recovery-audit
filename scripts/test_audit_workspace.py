"""Focused offline tests; all identifiers are synthetic and generated in memory."""

import csv
import json
import os
from pathlib import Path
import tempfile
import unittest

import audit_workspace as audit


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.input = self.base / "addresses.json"
        self.run = self.base / "run"
        self.evm = "0x" + "a" * 40
        self.solana = "1" * 32
        self.starknet = "0x1"
        self.input.write_text(json.dumps({
            "evm": [self.evm], "solana": [self.solana], "starknet": [self.starknet],
        }), encoding="utf-8")

    def initialize(self):
        audit.init(self.input, self.run)
        return json.loads((self.run / "wallets.json").read_text()), json.loads((self.run / "ledger.json").read_text())

    def save_ledger(self, ledger):
        (self.run / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")

    def evidence(self):
        path = self.run / "evidence" / "observation.txt"
        path.write_text("synthetic observation", encoding="utf-8")
        return "evidence/observation.txt"

    def finding(self, evidence_ref=None):
        return {
            "id": "finding-1", "wallet_id": "evm-001", "network": "synthetic-network",
            "protocol": "synthetic-protocol", "asset": "synthetic-asset", "amount": "12.345",
            "classification": "claimable", "verification": "view_only",
            "evidence_refs": [evidence_ref or self.evidence()], "next_action": "manual review",
        }

    def test_init_deduplicates_within_ecosystem_only_and_preserves_case(self):
        mixed = "0x" + "A" * 40
        self.input.write_text(json.dumps({
            "evm": [mixed, mixed.lower()], "solana": [self.solana],
            "starknet": ["0x01", "0x1"],
        }), encoding="utf-8")
        wallets, ledger = self.initialize()
        self.assertEqual([wallet["wallet_id"] for wallet in wallets["wallets"]], ["evm-001", "solana-001", "starknet-001"])
        self.assertEqual(wallets["wallets"][0]["address"], mixed)
        self.assertEqual(wallets["wallets"][0]["normalized_address"], mixed.lower())
        self.assertEqual(wallets["wallets"][2]["normalized_address"], "0x" + "0" * 63 + "1")
        self.assertEqual(ledger["findings"], [])
        audit.validate(self.run)

    def test_invalid_address_and_required_ecosystem_keys(self):
        for payload in (
            {"evm": ["0x" + "g" * 40], "solana": [], "starknet": []},
            {"evm": [], "solana": ["0" * 32], "starknet": []},
            {"evm": [], "solana": [], "starknet": ["0x0"]},
            {"evm": [], "solana": []},
        ):
            with self.subTest(payload=payload), self.assertRaises(audit.AuditError):
                self.input.write_text(json.dumps(payload), encoding="utf-8")
                audit.init(self.input, self.run)
            self.assertFalse(self.run.exists())

    def test_no_overwrite_and_skill_root_containment(self):
        self.initialize()
        with self.assertRaises(audit.AuditError):
            audit.init(self.input, self.run)
        outside_alias = self.base / "skill-link"
        outside_alias.symlink_to(audit.SKILL_ROOT, target_is_directory=True)
        with self.assertRaises(audit.AuditError):
            audit.init(self.input, outside_alias / "synthetic-run")
        with self.assertRaises(audit.AuditError):
            audit.init(audit.SKILL_ROOT / "SKILL.md", self.base / "another-run")
        broken_alias = self.base / "broken-run-link"
        broken_alias.symlink_to(self.base / "missing-target", target_is_directory=True)
        with self.assertRaises(audit.AuditError):
            audit.init(self.input, broken_alias)

    @unittest.skipUnless(os.name == "posix", "POSIX permission modes")
    def test_private_modes(self):
        self.initialize()
        for name in ("", "evidence", "reports"):
            self.assertEqual(((self.run / name).stat().st_mode & 0o777), 0o700)
        for name in ("wallets.json", "ledger.json"):
            self.assertEqual(((self.run / name).stat().st_mode & 0o777), 0o600)

    def test_bool_schema_versions_rejected(self):
        wallets, ledger = self.initialize()
        wallets["schema_version"] = True
        (self.run / "wallets.json").write_text(json.dumps(wallets), encoding="utf-8")
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)
        wallets["schema_version"] = 1
        (self.run / "wallets.json").write_text(json.dumps(wallets), encoding="utf-8")
        ledger["schema_version"] = True
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)

    def test_manual_duplicate_canonical_wallet_rejected(self):
        wallets, _ = self.initialize()
        duplicate = dict(wallets["wallets"][0])
        duplicate["wallet_id"] = "evm-002"
        duplicate["address"] = duplicate["address"].upper().replace("0X", "0x")
        duplicate["normalized_address"] = self.evm
        wallets["wallets"].append(duplicate)
        (self.run / "wallets.json").write_text(json.dumps(wallets), encoding="utf-8")
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)

    def test_decimal_float_and_provider_only_claimable_rejected(self):
        _, ledger = self.initialize()
        ledger["findings"] = [self.finding()]
        self.save_ledger(ledger)
        audit.validate(self.run)
        ledger["findings"][0]["amount"] = 1.25
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)
        ledger["findings"][0]["amount"] = "1.25"
        ledger["findings"][0]["verification"] = "provider_reported"
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)

    def test_evidence_traversal_and_symlink_escape_rejected(self):
        _, ledger = self.initialize()
        ledger["findings"] = [self.finding()]
        ledger["findings"][0]["evidence_refs"] = ["../outside.txt"]
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)
        outside = self.base / "outside.txt"
        outside.write_text("synthetic", encoding="utf-8")
        (self.run / "evidence" / "escape.txt").symlink_to(outside)
        ledger["findings"][0]["evidence_refs"] = ["evidence/escape.txt"]
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)

    def test_ledger_symlink_escape_rejected(self):
        self.initialize()
        outside = self.base / "other-ledger.json"
        outside.write_text("{}", encoding="utf-8")
        (self.run / "ledger.json").unlink()
        (self.run / "ledger.json").symlink_to(outside)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)

    def test_coverage_counts_and_paid_bridge_require_evidence(self):
        _, ledger = self.initialize()
        ledger["coverage"] = [{
            "id": "coverage-1", "ecosystem": "evm", "network": "synthetic-network",
            "surface": "logs", "status": "complete", "attempted": 2, "succeeded": 1,
            "failed": 1, "not_attempted": 0, "notes": "", "evidence_refs": [],
        }]
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)
        ledger["coverage"][0].update(status="partial")
        ledger["bridges"] = [{
            "id": "bridge-1", "source_wallet_id": "evm-001", "source_network": "synthetic-origin",
            "destination_network": "synthetic-destination", "source_tx": "synthetic-source-id",
            "destination_tx": None, "status": "paid_exact", "evidence_refs": [], "notes": "",
        }]
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)

    def test_export_escapes_formula_and_keeps_full_address(self):
        _, ledger = self.initialize()
        ledger["findings"] = [self.finding()]
        ledger["findings"][0]["protocol"] = "=synthetic_formula()"
        ledger["findings"][0]["notes"] = "  @synthetic"
        ledger["findings"][0]["quoted_value"] = "120.50"
        ledger["findings"][0]["quote_currency"] = "synthetic-unit"
        ledger["findings"][0]["quote_at_utc"] = "2026-01-01T00:00:00Z"
        self.save_ledger(ledger)
        audit.export(self.run)
        with (self.run / "reports" / "recovery-ledger.csv").open(newline="", encoding="utf-8") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["wallet_address"], self.evm)
        self.assertEqual(row["protocol"], "'=synthetic_formula()")
        self.assertEqual(row["notes"], "'  @synthetic")
        self.assertEqual(row["amount"], "12.345")
        self.assertEqual(row["quoted_value"], "120.50")
        self.assertEqual(row["quote_currency"], "synthetic-unit")
        self.assertEqual(row["quote_at_utc"], "2026-01-01T00:00:00Z")
        audit.export(self.run)

    def test_quote_requires_currency_and_utc_time(self):
        _, ledger = self.initialize()
        ledger["findings"] = [self.finding()]
        quote = ledger["findings"][0]
        quote["quoted_value"] = "10.00"
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)
        quote["quote_currency"] = "synthetic-unit"
        quote["quote_at_utc"] = "2026-01-01T00:00:00+01:00"
        self.save_ledger(ledger)
        with self.assertRaises(audit.AuditError):
            audit.validate(self.run)
        quote["quote_at_utc"] = "2026-01-01T00:00:00Z"
        self.save_ledger(ledger)
        audit.validate(self.run)


if __name__ == "__main__":
    unittest.main()
