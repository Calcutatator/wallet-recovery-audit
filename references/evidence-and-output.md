# Evidence and deliverables

## Evidence record

Every numerical claim needs exact asset identity (chain plus token/program/account), decimals/base units, owner/authority, block/slot and UTC observation time. Save raw requests/responses and interpretation separately. Provider URLs must be credential-free. When block pinning is unavailable, label latest-state and record the actual slot/header if exposed; never pretend independent reads were atomic.

Use [data-format.md](data-format.md) for the compact ledger, with richer raw records under `evidence/`. Amounts are decimal strings or explicit unknowns, never binary floating-point arithmetic. Retain base-unit and human-unit values in evidence. Give findings local evidence references; primary web links help readers but do not replace saved volatile responses.

| Observation | Permitted conclusion | Does not establish |
|---|---|---|
| Exact state getter, valid current layout | Current recorded balance or right | Backing, cash value or exit success |
| Full unsigned exit simulation | Execution under that state and recorded assumptions | Signer access, broadcast, inclusion or future result |
| Successful receipt and asset credit | Historical payment to evidenced recipient | Present balance or recipient control |
| Provider completed plus hashes | Provider-reported settlement lead | Independently verified destination payment |
| Matching asset/amount/time/provider/recipient | Qualified high-confidence reconciliation | Exact message/order-ID proof |
| Source deposit or spending history | Historical contribution | Current refund, equity or recoverable principal |
| Missing index, denied API, reverted getter, no quote | Coverage/route limitation with a reason | Zero balance or no entitlement |
| Storage-derived accounting | Inference under verified layout/formula and controls | A direct getter or simulation never performed |

User attribution can settle a holding's classification (for example, a known loss replaced by a debt token). Label it separately from on-chain facts; do not repeat the same ownership/relationship question after clarification.

## Run files

Keep each audit outside the installed skill:

- `wallets.json`: full inputs, canonical forms and scope/ownership provenance.
- `ledger.json`: structured findings, coverage and bridge reconciliations.
- `evidence/`: credential-free requests, snapshots, receipts, decoded records and unsigned simulations.
- `reports/report.md`: final combined report with evidence and ecosystem-detail links.
- `reports/evm.md`, `reports/solana.md`, `reports/starknet.md`: only for supplied ecosystems; exact methods and limits.
- `reports/recovery-ledger.csv`: one asset/right per finding, full address, classification, verification, next action and evidence. Split multiple paid assets into rows sharing a claim/position ID to prevent duplication.
- `reports/wallet-directory.csv`, `reports/coverage.csv`, `reports/bridge-reconciliation.csv`: full addresses and scoped counts/statuses, exported from the validated ledger.

Add per-position or per-account inventories when they make recovery concrete: liquidity NFT IDs, empty token accounts, vesting stream IDs. Keep raw response dumps out of narrative reports. Never include private run data in a skill archive or installation.

## Combined report order

1. **Practical action list:** present claims ranked by realizable value and effort. Full copyable wallet, network, protocol, amount, proof level, fee/delay and next step.
2. **Managed positions and ordinary balances:** distinct from newly found recoveries. Surface obscure holdings without calling them stuck.
3. **Future, unpriced or impaired rights:** locks, unavailable backing, debt/recovery tokens, ownership constraints. Known losses stay out of available-money totals.
4. **Bridge reconciliations:** historical payments, verified pending/refundable messages and unknowns. Exact source/destination records.
5. **Remaining leads:** the missing evidence and how to resolve it, without assigning historical input as a claim.
6. **Coverage/methods:** attempted networks, fresh/stale heads, provider failures, bodies decoded versus discovered, scoped protocol queries, pagination boundaries and sampling.
7. **Full address directory:** all supplied/confirmed accounts by ecosystem. An actionable wallet must never be identified only by a number or ellipsis.

Use full addresses in inline code in every action row or claim card. Preserve base58 case. Explorer links may accompany addresses but must not be the only copyable representation. Wallet numbers are secondary and scoped by ecosystem. Chat links to local files use absolute paths; generated reports can use verified relative links.

Explain failed withdrawals when they change priority. Failed routes, unpriced holdings and inactive contracts stay in the ledger. State that simulations are unsigned and no funds were moved.

## Valuation and duplicate checks

- Separate token units from indicative quotes. Record `quoted_value`, `quote_currency` and `quote_at_utc` together in the ledger, with exact input size, route and output asset in evidence. A marginal price multiplied by a large balance is not a full-size exit estimate.
- Net fees only when modeled; otherwise label gross before gas/fees. Future unlock/sale estimates are not current cash.
- Do not add one right as receipt shares, converted underlying, staked receipt, recovery debt and historical deposit. Use common claim/position IDs and notes.
- Do not add independent quotes consuming the same shallow liquidity without a combined-size quote.
- Stablecoin units may be shown at face value for orientation, with exact asset/bridge identity; avoid implying guaranteed redemption or a verified peg.
- Liquid balance, rent, staked principal, rewards and protocol-owned collateral are different categories. Confirm a closure returns rent to the stated recipient.
- NFT floors, asking prices and mint costs are not executable proceeds. Report token-specific bids and depth when verified.

## Final validation

The helper checks schema, decimals, wallet references, evidence paths and counters; it does not prove observations true or discovery complete. Independently review highest-value claims and storage reconstruction where practical.

When a later ecosystem resolves an earlier question, update the main report and linked detail or mark the old text explicitly superseded. Record user corrections locally. Preserve snapshot times when figures change.

Before execution guidance, recheck the sender, asset, claim state and fee path. If already paid, mark paid and link the receipt instead of repeating the claim. Writing reports does not imply recurring scans.
