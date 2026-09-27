# Solana and SVM read-only audit procedure

Use this reference for an evidence-bounded search for forgotten value on Solana or a Solana Virtual Machine (SVM) network. The main skill governs intake, privacy, and output. Never submit a transaction during this procedure. Recheck current official chain, program, and protocol documentation before interpreting state or preparing a later action.

## Establish the network and authority set

1. Record the RPC network, genesis hash, commitment, and returned context slot or block height. Standard Solana account reads generally cannot be pinned to an arbitrary historical slot: `minContextSlot` is a lower bound, not a snapshot pin. Record the actual context of each response and any slot drift; use supported archival snapshots only when available. Check explorer and RPC against canonical chain documentation. SVM address format does not establish Solana mainnet.
2. Record each supplied public key and its provenance. For related keys, use public wallet descriptors, explicit user confirmation and documented derivation inputs; never access or derive from a seed/private key in this audit. A signer for one key does not prove control of related keys, program-derived addresses (PDAs), treasuries or multisigs.
3. Separate four questions: where assets are held, which account or program owns the state, which authority can change it, and who can pay fees. Note missing signer or policy information as an authority gap.
4. Keep a source log: provider, method, parameters, pinned slot, page cursor, returned count, failures, retries, and independent cross-checks. A failed, truncated, or unsupported query is **unknown**, never zero.

## Direct accounts and token programs

5. Read system account lamports and executable/program status at the pinned commitment. Do not treat an uncreated address as evidence that no derived or program-held assets exist.
6. Query token accounts **by owner** under both the classic SPL Token program and Token Extensions (Token-2022) program. Include associated and non-associated token accounts; do not infer coverage from a wallet UI token list.
7. For each token account, verify program owner, account owner, mint, raw amount, decimals, state, delegate and allowance, close authority, and native-wrapped status. Read the mint and any relevant extensions before assigning recoverability.
8. Check Token-2022 transfer fees, withheld amounts, freezes/default state, permanent delegates, transfer hooks, confidential or nontransferable features, and any other active extension. An amount may be visible while transfer or close rights differ.
9. Track token-account rent separately with an explicit close-authority and fee check. Standard token account lamports and token quantity are distinct; wrapped-native accounts need special care because account lamports also include the underlying native asset. Never count that same wrapped principal twice.
10. Validate empty-account closure from live account state: zero token amount alone may be insufficient if withheld fees, native wrapping, extensions, close authority, or program rules prevent closing. State a close estimate only after verifying those conditions.
11. Check whether a keepalive fee payer is available for later account closure or claim transactions. Model transaction fees separately from the recoverable balance; do not imply a zero-SOL wallet can necessarily self-fund a close.

## Stake and non-wallet ownership

12. Enumerate stake accounts by authorized staker and withdrawer where supported; supplement with historical creation and authority-change evidence. Inspect lockup, delegation, activation/deactivation, rewards, withdraw authority, and unbond or cooldown state.
13. Distinguish delegated stake, inactive/withdrawable stake, rewards already incorporated into stake, and pending deactivation. Avoid counting the same lamports as both stake principal and wallet SOL.
14. For program-held funds, derive only protocol PDAs whose seeds, program ID, layout, version, and discriminator can be verified from current primary sources or audited code. Confirm each candidate account's owner and decoded authority fields on chain.
15. A PDA matching a plausible seed is only a candidate. Link it to the wallet through stored authority, position owner, receipt asset, or documented access-control path. Separate wallet control from protocol custody and multisig governance.
16. Inspect protocol families relevant to observed transactions and receipts: lending deposits and debt, vault shares, liquidity pools, farms, vesting, escrows, bridges, and derivatives. Report gross assets, liabilities, claimable rewards, and withdrawal constraints separately.
17. For concentrated or discrete liquidity (CLMM/DLMM), enumerate position accounts or position NFTs, pool and bin/tick ranges, liquidity, uncollected fees, and rewards. Position-token ownership alone does not establish current principal value; use current pool state and protocol math.
18. Inspect treasury and multisig programs when the key appears as owner, member, proposer, or signer. Verify threshold, transaction state, time locks, and who can execute; do not present treasury balances as personally spendable.
19. Private or app-specific perpetuals and trading venues may hold margin beyond public deposit accounts. Use documented subaccount derivation, authenticated read-only account views where authorized, or verified on-chain layouts. Mark inaccessible private state as a coverage gap.

## NFTs and compressed assets

20. Include classic token NFTs, programmable or Core-style assets, and compressed assets. Distinguish ownership of a collectible from ownership of an LP position, claim ticket, or other financial right.
21. For compressed assets, use a current Digital Asset Standard (DAS) or equivalent index with documented tree and proof verification; a normal token-account query cannot establish absence.
22. Cross-check discovered assets with on-chain collection, tree, leaf, and authority data where available. Note index freshness and whether the provider covers the target network and historical trees.
23. Treat NFT metadata and displayed floor prices as context, not as a realizable wallet balance. For financial NFTs, decode the underlying position and its exit conditions.

## History and coverage

24. Paginate `getSignaturesForAddress` to the intended historical boundary for every key and relevant account. Record oldest/newest signatures, page sizes, repeated boundaries, and provider retention limits.
25. Keep **signature coverage** separate from **decoded transaction coverage**. A complete signature list with only a fraction of transactions fetched or parsed is not complete transaction analysis.
26. Fetch transactions with supported version settings and inspect top-level and inner instructions, account keys, logs, token balance changes, and status. Preserve parse failures and unavailable transactions as explicit counts.
27. Use history to discover programs and accounts for targeted reads; do not assume present-day balances can be reconstructed by summing transfers. Reorganizations, rent, rewards, wrapped SOL, and program internal accounting require current state.
28. Build a program-coverage register: program family, discovery path, decoder/version source, wallets/accounts checked, current-state result, history checked, and unresolved gaps. Prioritize programs actually touched by the key, while documenting broader scans separately.
29. Cross-check material candidates against an independent RPC or explorer at a comparable finalized slot. If providers disagree, preserve both observations and investigate before concluding.
30. End each category as verified positive, verified zero within stated scope, or unknown. A "no forgotten funds" conclusion requires all relevant categories and pagination/decoding limits to be disclosed.

## Completion checks by evidence type

- **Network:** Chain identity and finalized reference slot were independently checked.
- **Keys:** Every supplied public key has a provenance and derivation or signer-control status.
- **System SOL:** The wallet account and material auxiliary accounts were read at the reference slot.
- **Classic tokens:** Owner queries completed for the SPL Token program, with account totals and failures logged.
- **Token-2022:** Owner queries completed for the Token Extensions program, with extensions decoded or listed as unknown.
- **Authorities:** Each nonzero asset has a verified owner, delegate, freeze, close, and protocol withdrawal path as applicable.
- **Rent:** Recoverable rent is backed by a specific closable account and a tested interpretation of close rules.
- **Stake:** Stake-account search covers both staker and withdrawer roles, plus authority changes found in history.
- **NFTs:** Classic, Core-style, and compressed scopes are each marked covered or unverified.
- **Positions:** Each receipt NFT or position PDA has current principal, fees, rewards, debt, and exit status checked.
- **Custody:** Treasury, multisig, and program escrow balances are classified by actual authorization rights.
- **History:** Signature pages reach the stated boundary; missing historical retention is named.
- **Decoding:** Transaction-fetch and decode fractions are reported independently from signature completion.
- **Programs:** Every discovered protocol program is either examined or entered as an explicit gap.
- **Cross-check:** Material positive and zero conclusions have a second source or a documented reason one is unavailable.

For every candidate, keep a compact evidence row with `chain`, `slot`, `account`, `program`, `asset`, `raw amount`, `unit`, `authority`, `claim path`, `source`, and `confidence`. Preserve raw units until mint decimals and program accounting are confirmed. A source row may show the same economic value in a receipt token and an underlying position; mark those as linked representations so they are not summed.

When a provider imposes pagination or historical-retention limits, run the remaining targeted reads through a second archival source if available. If no complete source exists, record the oldest covered slot and the exact unexamined interval. An explorer's displayed transaction count is not proof that all inner instructions or protocol accounts were decoded.

If protocol documentation changed after a position was opened, select the deployed program version that governed the account at the reference slot. Verify account discriminator and length before decoding. A decoder that accepts an account without checking these fields is insufficient for a zero or withdrawal conclusion.

Record a proposed recovery path only as a read-only feasibility assessment: required signer and fee payer, account state changes, cooldowns, sequence of instructions, and likely fees. Do not equate possible closure or claimability with a guaranteed net recovery; later execution can face changed state, fees, or permissions.

## Source anchors to revisit

- [Solana JSON-RPC methods](https://solana.com/docs/rpc/http) for account reads, token-owner queries, transaction reads, and signature pagination.
- [Token basics](https://solana.com/docs/tokens/basics) and [Token Extensions](https://solana.com/docs/tokens/extensions) for account authorities, closure, and extension semantics.
- [Solana CLI reference](https://solana.com/docs/references/solana-cli) and current staking documentation for stake lifecycle and authority operations.
- Current official documentation and verified source for each observed protocol or asset standard; record the exact version and block used. A general guide cannot certify a protocol's present layout.
