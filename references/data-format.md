# Offline audit workspace format

This helper creates a local, read-only audit workspace from addresses supplied for the current run. It does not discover chains, query providers, sign, broadcast, track in the background, or assert that a finding is true. An analyst must collect and cite evidence using the skill's chain guides. Keep input and run directories outside this skill package.

## Commands

```text
python3 scripts/audit_workspace.py init --addresses INPUT_JSON --out RUN_DIR
python3 scripts/audit_workspace.py validate --run RUN_DIR
python3 scripts/audit_workspace.py export --run RUN_DIR
```

`init` requires a new `RUN_DIR` and refuses an existing directory or symlink. It creates `wallets.json`, `ledger.json`, `evidence/`, and `reports/`. On POSIX systems the run and child directories are mode `0700`; created JSON and CSV files are mode `0600`. The input JSON and output run must resolve outside the skill root, including through symlinks. Store supporting source captures in `evidence/`, then edit `ledger.json` manually. `validate` checks structure and local evidence references. `export` validates first and writes four CSVs under `reports/`; rerunning it may replace only those generated CSVs. It never edits the input, ledger, or evidence.

The address input is an object with exactly these three arrays, including empty arrays:

```json
{"evm": [], "solana": [], "starknet": []}
```

Each entry is a string. EVM accepts `0x` plus 40 hexadecimal digits, preserves supplied case, and deduplicates case-insensitively. Starknet accepts a nonzero hexadecimal integer below `2^251 - 256`, preserves the supplied spelling, normalizes to `0x` plus 64 lowercase hexadecimal digits, and deduplicates only inside Starknet. Solana accepts base58 that decodes to exactly 32 bytes and preserves case. The helper checks syntax, not EVM checksum, key control, ownership, or whether an address exists on-chain. It never merges identities across ecosystems.

## `wallets.json`

`schema_version` is integer `1`, not a Boolean. `wallets` is an array of entries with `wallet_id` (for example, `evm-001`), `ecosystem`, `address`, `normalized_address`, and `ownership: "user_supplied"`. IDs and canonical addresses within each ecosystem are unique in the run, including after manual edits. An address in this file is only a user-supplied search seed. For a bridge destination or smart account, ownership requires separate evidence.

## `ledger.json`

The top-level object has integer `schema_version: 1` (a Boolean is invalid), `observations_at_utc` as an ISO 8601 UTC timestamp ending in `Z`, and arrays `findings`, `coverage`, and `bridges`. All IDs within each array must be unique. `evidence_refs` are arrays of existing relative file paths within the run; absolute paths, `..` traversal, and symlink escapes fail validation. `source_urls` may be included as an array of HTTP(S) URLs for attribution; URLs are not fetched or treated as local evidence by the helper.

Each finding requires `id`, `wallet_id`, `network`, `protocol`, `asset`, `amount`, `classification`, `verification`, `evidence_refs`, and `next_action`. `amount` is a nonnegative decimal string such as `"0"` or `"12.345"`, or `null` when unknown; JSON numeric values, signs, exponent notation, and floats are invalid. Optional fields are `contract_or_account`, `position_id`, `quoted_value` (same decimal-string rule or `null`), `quote_currency`, `quote_at_utc`, and `notes`. A non-null `quoted_value` requires a nonempty `quote_currency` and valid UTC `quote_at_utc`; both are exported. `source_urls` may be added. A quote should describe the current full-size position at its stated time, with liabilities and claim collisions explained in notes or supporting evidence.

`classification` is one of `claimable`, `withdrawable_after_delay`, `managed_position`, `ordinary_holding`, `unpriced_right`, `future_vesting`, `stranded`, `known_loss`, or `unresolved`. `verification` is one of `view_only`, `simulated`, `paid`, `provider_reported`, `storage_derived`, or `unknown`. Every classification except `unresolved` needs an evidence file. `claimable` additionally requires an amount and evidence, and cannot use `provider_reported` or `unknown` verification. These checks prevent a few overclaims; they do not certify economic recoverability or ownership.

Each coverage row requires `id`, `ecosystem`, `network`, `surface`, `status`, `attempted`, `succeeded`, `failed`, `not_attempted`, `notes`, and `evidence_refs`. Status is `complete`, `partial`, `blocked`, or `not_attempted`. Counts are nonnegative integers, with `attempted = succeeded + failed`; `complete` requires zero failed and zero not attempted. Use separate rows for distinct query surfaces and record provider errors, pagination gaps, stale heads, and unsearched ranges rather than inferring zero assets.

Each bridge row requires `id`, `source_wallet_id`, `source_network`, `destination_network`, `source_tx`, `destination_tx` (string or `null`), `status`, `evidence_refs`, and `notes`. Status is `paid_exact`, `paid_high_confidence`, `provider_completed`, `pending_verified`, `refunded`, `source_reverted`, or `unknown`. A paid status needs a destination transaction and evidence; verified pending, refunded, and source-reverted statuses need evidence. A provider's `completed` report alone does not prove recipient credit. Match source and destination with protocol IDs and exact receipts where possible; an old source deposit is not proof of a current refund.

Optional bridge fields are `destination_wallet_id` and `recipient_address` with `recipient_ownership_notes`. A destination wallet ID must reference a wallet in this run. `recipient_address` may hold a full unconfirmed destination address; ownership notes are required when it is present. Do not infer that a destination smart account belongs to the source wallet.

## CSV export and handling

`export` produces `recovery-ledger.csv`, `wallet-directory.csv`, `coverage.csv`, and `bridge-reconciliation.csv`. The finding and bridge CSVs include full wallet-address columns so reviewers can disambiguate rows. No grand cash total is calculated because shares, collateral, bridge representations, and claims can overlap. CSV text beginning with spreadsheet formula characters (including after leading spaces) is escaped for safer opening in spreadsheet software. Review the JSON and cited evidence before acting; the helper never performs financial execution.

Write the narrative Markdown audit report manually from verified evidence and the skill's reporting guidance; this helper deliberately does not generate conclusions or a report.
