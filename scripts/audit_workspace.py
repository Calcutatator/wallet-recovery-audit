#!/usr/bin/env python3
"""Offline, standard-library workspace helper for a read-only wallet audit."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import re
import sys
import tempfile


SKILL_ROOT = Path(__file__).resolve().parents[1]
ECOSYSTEMS = ("evm", "solana", "starknet")
CLASSIFICATIONS = frozenset((
    "claimable", "withdrawable_after_delay", "managed_position", "ordinary_holding",
    "unpriced_right", "future_vesting", "stranded", "known_loss", "unresolved",
))
VERIFICATIONS = frozenset((
    "view_only", "simulated", "paid", "provider_reported", "storage_derived", "unknown",
))
COVERAGE_STATUSES = frozenset(("complete", "partial", "blocked", "not_attempted"))
BRIDGE_STATUSES = frozenset((
    "paid_exact", "paid_high_confidence", "provider_completed", "pending_verified",
    "refunded", "source_reverted", "unknown",
))
EVM_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
STARKNET_RE = re.compile(r"^0x[0-9a-fA-F]+$")
DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class AuditError(ValueError):
    """Invalid input or unsafe workspace path."""


def fail(message: str) -> None:
    raise AuditError(message)


def required(mapping: dict, key: str, kind: type, context: str):
    value = mapping.get(key)
    if type(value) is not kind:
        fail(f"{context}.{key} must be {kind.__name__}")
    return value


def nonempty(mapping: dict, key: str, context: str) -> str:
    value = required(mapping, key, str, context)
    if not value.strip():
        fail(f"{context}.{key} must be nonempty")
    return value


def object_value(value, context: str) -> dict:
    if type(value) is not dict:
        fail(f"{context} must be an object")
    return value


def list_value(mapping: dict, key: str, context: str) -> list:
    return required(mapping, key, list, context)


def outside_skill(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    if resolved == SKILL_ROOT or SKILL_ROOT in resolved.parents:
        fail(f"{label} cannot be inside the skill root")
    return resolved


def normalize_address(ecosystem: str, address: str) -> str:
    if ecosystem == "evm":
        if not EVM_RE.fullmatch(address):
            fail("invalid EVM address: expected 0x and 40 hexadecimal digits")
        return address.lower()
    if ecosystem == "starknet":
        if not STARKNET_RE.fullmatch(address):
            fail("invalid Starknet address: expected a hexadecimal integer")
        number = int(address[2:], 16)
        if number <= 0 or number >= 2**251 - 256:
            fail("Starknet address is outside the valid field range")
        return "0x" + format(number, "064x")
    if ecosystem == "solana":
        if not address or any(char not in BASE58 for char in address):
            fail("invalid Solana address: expected base58")
        number = 0
        for char in address:
            number = number * 58 + BASE58.index(char)
        raw = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
        raw = b"\0" * (len(address) - len(address.lstrip("1"))) + raw
        if len(raw) != 32:
            fail("invalid Solana address: decoded length must be 32 bytes")
        return address
    fail(f"unsupported ecosystem: {ecosystem}")


def read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle, parse_float=lambda _: fail("JSON floats are not allowed"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"cannot read valid JSON at {path}: {error}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def check_utc(value: str, context: str) -> None:
    if not value.endswith("Z"):
        fail(f"{context} must be a UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        fail(f"{context} must be a valid UTC timestamp")


def private_json(path: Path, value: dict) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.chmod(path, 0o600)


def init(input_path: Path, out: Path) -> None:
    if os.path.lexists(out.expanduser()):
        fail("output run directory already exists")
    input_path = outside_skill(input_path, "input")
    out = outside_skill(out, "output")
    if os.path.lexists(out):
        fail("output run directory already exists")
    if not out.parent.is_dir():
        fail("output parent directory must already exist")
    if not input_path.is_file():
        fail("input must be a JSON file")
    payload = object_value(read_json(input_path), "input")
    if set(payload) != set(ECOSYSTEMS):
        fail("input must contain exactly evm, solana, and starknet arrays")
    wallets = []
    for ecosystem in ECOSYSTEMS:
        addresses = list_value(payload, ecosystem, "input")
        seen = set()
        for address in addresses:
            if type(address) is not str:
                fail(f"input.{ecosystem} entries must be strings")
            normalized = normalize_address(ecosystem, address)
            if normalized in seen:
                continue
            seen.add(normalized)
            wallets.append({
                "wallet_id": f"{ecosystem}-{len(seen):03d}",
                "ecosystem": ecosystem,
                "address": address,
                "normalized_address": normalized,
                "ownership": "user_supplied",
            })
    out.mkdir(mode=0o700, parents=False)
    os.chmod(out, 0o700)
    for child in ("evidence", "reports"):
        directory = out / child
        directory.mkdir(mode=0o700)
        os.chmod(directory, 0o700)
    private_json(out / "wallets.json", {"schema_version": 1, "wallets": wallets})
    private_json(out / "ledger.json", {
        "schema_version": 1, "observations_at_utc": utc_now(),
        "findings": [], "coverage": [], "bridges": [],
    })


def check_decimal(value, context: str, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if type(value) is not str or not DECIMAL_RE.fullmatch(value):
        fail(f"{context} must be an exact nonnegative decimal string")
    if not Decimal(value).is_finite():
        fail(f"{context} must be finite")


def check_evidence(run: Path, refs, context: str) -> list[str]:
    if type(refs) is not list:
        fail(f"{context} must be an array")
    checked = []
    for ref in refs:
        if type(ref) is not str or not ref or Path(ref).is_absolute() or ".." in Path(ref).parts:
            fail(f"{context} contains an unsafe relative path")
        target = (run / ref).resolve(strict=False)
        if run not in target.parents or not target.is_file():
            fail(f"{context} must refer to an existing file within the run")
        checked.append(ref)
    return checked


def check_source_urls(row: dict, context: str) -> None:
    if "source_urls" in row:
        urls = row["source_urls"]
        if type(urls) is not list or any(type(url) is not str or not url.startswith(("https://", "http://")) for url in urls):
            fail(f"{context}.source_urls must be an array of HTTP(S) URLs")


def run_json(run: Path, filename: str) -> dict:
    path = run / filename
    if path.is_symlink() or not path.is_file():
        fail(f"{filename} must be a regular file within the run")
    return object_value(read_json(path), filename)


def check_ids(items: list, kind: str) -> None:
    seen = set()
    for item in items:
        key = nonempty(item, "id", kind)
        if key in seen:
            fail(f"duplicate {kind} id: {key}")
        seen.add(key)


def validate(run_path: Path) -> tuple[dict, dict]:
    run = outside_skill(run_path, "run")
    if not run.is_dir():
        fail("run must be a directory")
    wallets_doc = run_json(run, "wallets.json")
    ledger = run_json(run, "ledger.json")
    if type(wallets_doc.get("schema_version")) is not int or wallets_doc["schema_version"] != 1:
        fail("wallets.json schema_version must be integer 1")
    if type(ledger.get("schema_version")) is not int or ledger["schema_version"] != 1:
        fail("schema_version must be 1")
    wallets = list_value(wallets_doc, "wallets", "wallets.json")
    wallet_ids = set()
    wallet_keys = set()
    for index, raw in enumerate(wallets):
        wallet = object_value(raw, f"wallets[{index}]")
        wid = nonempty(wallet, "wallet_id", "wallet")
        ecosystem = nonempty(wallet, "ecosystem", "wallet")
        if ecosystem not in ECOSYSTEMS or wid in wallet_ids:
            fail("invalid or duplicate wallet identity")
        wallet_ids.add(wid)
        address = nonempty(wallet, "address", "wallet")
        normalized = normalize_address(ecosystem, address)
        if nonempty(wallet, "normalized_address", "wallet") != normalized:
            fail("wallet normalized_address does not match address")
        if (ecosystem, normalized) in wallet_keys:
            fail("duplicate wallet address within ecosystem")
        wallet_keys.add((ecosystem, normalized))
        if wallet.get("ownership") != "user_supplied":
            fail("wallet ownership must be user_supplied")
    check_utc(nonempty(ledger, "observations_at_utc", "ledger"), "observations_at_utc")
    findings = list_value(ledger, "findings", "ledger")
    coverage = list_value(ledger, "coverage", "ledger")
    bridges = list_value(ledger, "bridges", "ledger")
    for kind, items in (("finding", findings), ("coverage", coverage), ("bridge", bridges)):
        for index, raw in enumerate(items):
            object_value(raw, f"{kind}[{index}]")
        check_ids(items, kind)
    for finding in findings:
        fid = finding["id"]
        check_source_urls(finding, fid)
        if nonempty(finding, "wallet_id", fid) not in wallet_ids:
            fail(f"{fid} references an unknown wallet")
        for key in ("network", "protocol", "asset", "next_action"):
            nonempty(finding, key, fid)
        classification = nonempty(finding, "classification", fid)
        verification = nonempty(finding, "verification", fid)
        if classification not in CLASSIFICATIONS or verification not in VERIFICATIONS:
            fail(f"{fid} has an invalid classification or verification")
        if "amount" not in finding:
            fail(f"{fid}.amount is required (use null when unknown)")
        check_decimal(finding["amount"], f"{fid}.amount", nullable=True)
        refs = check_evidence(run, finding.get("evidence_refs"), f"{fid}.evidence_refs")
        if classification != "unresolved" and not refs:
            fail(f"{fid} requires evidence")
        if classification == "claimable" and (finding["amount"] is None or not refs or verification in ("provider_reported", "unknown")):
            fail(f"{fid} claimable requires amount and direct evidence")
        for key in ("contract_or_account", "position_id", "quote_currency", "notes"):
            if key in finding and type(finding[key]) is not str:
                fail(f"{fid}.{key} must be a string")
        if "quoted_value" in finding:
            check_decimal(finding["quoted_value"], f"{fid}.quoted_value", nullable=True)
            if finding["quoted_value"] is not None:
                nonempty(finding, "quote_currency", fid)
                check_utc(nonempty(finding, "quote_at_utc", fid), f"{fid}.quote_at_utc")
        if "quote_at_utc" in finding:
            check_utc(nonempty(finding, "quote_at_utc", fid), f"{fid}.quote_at_utc")
    for row in coverage:
        cid = row["id"]
        check_source_urls(row, cid)
        for key in ("ecosystem", "network", "surface", "status", "notes"):
            nonempty(row, key, cid) if key != "notes" else required(row, key, str, cid)
        if row["ecosystem"] not in ECOSYSTEMS or row["status"] not in COVERAGE_STATUSES:
            fail(f"{cid} has an invalid ecosystem or status")
        counts = [required(row, key, int, cid) for key in ("attempted", "succeeded", "failed", "not_attempted")]
        if any(count < 0 for count in counts) or counts[0] != counts[1] + counts[2]:
            fail(f"{cid} has inconsistent coverage counts")
        if row["status"] == "complete" and (counts[2] or counts[3]):
            fail(f"{cid} complete coverage has failures or unattempted work")
        if row["status"] == "not_attempted" and counts[0]:
            fail(f"{cid} not_attempted coverage has attempts")
        check_evidence(run, row.get("evidence_refs"), f"{cid}.evidence_refs")
    for bridge in bridges:
        bid = bridge["id"]
        check_source_urls(bridge, bid)
        if nonempty(bridge, "source_wallet_id", bid) not in wallet_ids:
            fail(f"{bid} references an unknown source wallet")
        if "destination_wallet_id" in bridge and bridge["destination_wallet_id"] is not None:
            if nonempty(bridge, "destination_wallet_id", bid) not in wallet_ids:
                fail(f"{bid} references an unknown destination wallet")
        for key in ("source_network", "destination_network", "source_tx", "status"):
            nonempty(bridge, key, bid)
        required(bridge, "notes", str, bid)
        if bridge["status"] not in BRIDGE_STATUSES:
            fail(f"{bid} has an invalid status")
        destination_tx = bridge.get("destination_tx")
        if destination_tx is not None and (type(destination_tx) is not str or not destination_tx.strip()):
            fail(f"{bid}.destination_tx must be a nonempty string or null")
        refs = check_evidence(run, bridge.get("evidence_refs"), f"{bid}.evidence_refs")
        if bridge["status"] in ("paid_exact", "paid_high_confidence") and (not destination_tx or not refs):
            fail(f"{bid} paid status requires destination_tx and evidence")
        if bridge["status"] in ("pending_verified", "refunded", "source_reverted") and not refs:
            fail(f"{bid} verified status requires evidence")
        if "recipient_address" in bridge:
            nonempty(bridge, "recipient_address", bid)
            nonempty(bridge, "recipient_ownership_notes", bid)
    return wallets_doc, ledger


def csv_safe(value) -> str:
    if value is None:
        return ""
    output = str(value)
    if output.lstrip().startswith(("=", "+", "-", "@")) or output.startswith(("\t", "\r", "\n")):
        return "'" + output
    return output


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".export-", suffix=".csv", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: csv_safe(row.get(field)) for field in fields})
        os.replace(temporary, path)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def export(run_path: Path) -> None:
    run = outside_skill(run_path, "run")
    wallets_doc, ledger = validate(run)
    reports = run / "reports"
    if reports.is_symlink() or not reports.is_dir() or reports.resolve() != reports:
        fail("reports must be a real directory within the run")
    wallet_map = {wallet["wallet_id"]: wallet for wallet in wallets_doc["wallets"]}
    specs = (
        ("wallet-directory.csv", ("wallet_id", "ecosystem", "address", "normalized_address", "ownership"), wallets_doc["wallets"]),
        ("recovery-ledger.csv", ("id", "wallet_id", "wallet_address", "network", "protocol", "asset", "amount", "classification", "verification", "contract_or_account", "position_id", "quoted_value", "quote_currency", "quote_at_utc", "evidence_refs", "next_action", "notes"), [
            {**item, "wallet_address": wallet_map[item["wallet_id"]]["address"], "evidence_refs": " | ".join(item["evidence_refs"])} for item in ledger["findings"]
        ]),
        ("coverage.csv", ("id", "ecosystem", "network", "surface", "status", "attempted", "succeeded", "failed", "not_attempted", "notes", "evidence_refs"), [
            {**item, "evidence_refs": " | ".join(item["evidence_refs"])} for item in ledger["coverage"]
        ]),
        ("bridge-reconciliation.csv", ("id", "source_wallet_id", "source_wallet_address", "destination_wallet_id", "destination_wallet_address", "recipient_address", "recipient_ownership_notes", "source_network", "destination_network", "source_tx", "destination_tx", "status", "evidence_refs", "notes"), [
            {**item, "source_wallet_address": wallet_map[item["source_wallet_id"]]["address"],
             "destination_wallet_address": wallet_map[item["destination_wallet_id"]]["address"] if item.get("destination_wallet_id") else "",
             "evidence_refs": " | ".join(item["evidence_refs"])} for item in ledger["bridges"]
        ]),
    )
    for filename, fields, rows in specs:
        target = reports / filename
        if target.is_symlink() or (target.exists() and not target.is_file()):
            fail(f"unsafe report target: {filename}")
        write_csv(target, fields, rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init_parser = commands.add_parser("init", help="create a private run from explicit address arrays")
    init_parser.add_argument("--addresses", type=Path, required=True)
    init_parser.add_argument("--out", type=Path, required=True)
    for name in ("validate", "export"):
        command = commands.add_parser(name)
        command.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init(args.addresses, args.out)
        elif args.command == "validate":
            validate(args.run)
        else:
            export(args.run)
    except (AuditError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
