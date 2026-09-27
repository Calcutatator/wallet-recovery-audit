# Starknet read-only audit procedure

Use this reference for an evidence-bounded search for forgotten value in the Starknet address namespace. The main skill governs intake, privacy, and output. Never submit a transaction during this procedure. Verify current official Starknet, RPC, account, and protocol sources before relying on ABI, storage, or fee behavior.

## Network, wallet, and transaction baseline

1. Record chain ID, RPC/spec version, block number and hash, finality status, and provider. Pin reads to the same block where the RPC permits it; record when a provider silently uses latest.
2. Keep Starknet addresses distinct from Ethereum addresses, even if a bridge or wallet displays both. Verify account-contract address derivation, deployment state, class hash, signer or guardian model, and whether the supplied wallet controls that exact account.
3. Distinguish contract deployment from spend authority. A counterfactual or undeployed account can receive assets, but later deployment and execution may require specific class, salt, signer, funding, and current account rules.
4. If an observed address differs from the expected wallet, debug chain ID, account implementation and version, salt, public key, deployer, proxy, derivation inputs, and formatting. Do not silently merge balances across addresses.
5. Reconstruct activity by transaction type: `DEPLOY_ACCOUNT`, `DECLARE`, `INVOKE`, and relevant L1 handlers. Paginate events and account transactions to the intended boundary; keep raw transaction count, decoded count, and parser failures separate.
6. For every transaction used as evidence, inspect receipt execution and finality status, revert reason, emitted events, fee, and calls where available. An attempted call or emitted intent does not prove successful state change.
7. Account nonce is a consistency check, not a complete activity index. Compare nonce progression with accepted invokes and deployment; explain gaps, version differences, reverted execution, and provider omissions instead of forcing a count to match.
8. Log every RPC method, block ID, page cursor, returned count, error, retry, and parser version. A call error, missing ABI, stale index, or unsupported method means **unknown**, never zero.

## Token and NFT state

9. Obtain candidate token contracts from receipt events, wallet history, verified registries, and observed protocol interactions. Avoid treating a fixed token catalog as exhaustive.
10. Resolve proxy implementation or class at the pinned block and use its current ABI. Try documented `balanceOf`/`balance_of` and related naming or argument conventions only as justified by the ABI; decode `u256`/felt values with verified decimals.
11. Compare current balance calls with receipt-derived transfers, mints, burns, bridge events, and protocol withdrawals. If an event points to a token omitted by an index, add the contract to direct reads and document the discrepancy.
12. Verify token contract identity, proxy upgrade path, blacklists, pauses, fee behavior, and transfer restrictions before describing a balance as recoverable. Do not assume an ERC-20-like interface is standard merely because a call returns a number.
13. Enumerate ERC-721/ERC-1155-like assets and protocol position NFTs from event history and supported indexers. Verify current owner/quantity at the pinned block and whether the NFT represents an active position.
14. A liquidity NFT with only accrued fees can still exist after principal removal; conversely, a burn or transfer event alone does not prove principal was withdrawn. Read the position state, ownership, principal, fees, and reward accounting directly.
15. Keep collectible market estimates outside verified liquid balances. For position NFTs, value claims using current pool state and protocol math, with debt and withdrawal limits shown separately.

## Protocol claims, orders, and custody

16. Follow observed contracts into lending, vaults, liquidity pools, staking, derivatives, bridges, escrows, and rewards. Confirm current deployed class, proxy target, ABI, and documented storage layout for the block under review.
17. For lending and vault shares, read shares and exchange rate or net asset value, underlying backing, debt, fees, withdrawal liquidity, pauses, and frozen status. A share balance is not the same as immediately liquid underlying.
18. For staking, enumerate all relevant pools or validators rather than one default pool. Verify stake owner, reward authority, accrued versus already-paid rewards, pending exits, unbonding, and claim windows.
19. For order books and derivatives, reconstruct order and position state from accepted receipts plus current contract reads. Catch up event/index cursors fully; separate open, filled, cancelled, expired, and reverted orders.
20. If an order or claim mapping lacks an ABI getter, use direct storage only when the slot formula and contract version are verified from current primary source. Then cross-check against receipt history and an independent decoder or reviewer.
21. Treat unexplained catch-up reverts, stale indexer state, and unknown storage formulas as unresolved. Do not turn a failed replay or guessed slot into a zero claim.
22. Identify withdrawal controls: wallet signer, account module, manager, multisig, timelock, bridge message, or protocol-specific role. Report protocol-held equity separately from an immediately executable wallet transfer.
23. Verify Merkle rewards through the correct root, epoch, leaf encoding, and proof, plus claimed bitmap or nonce. Missing proof data or an unavailable distributor is a proof gap, not evidence of no entitlement.
24. Check appchain or external domain positions only when documented address mapping, bridge accounting, and data access are available. An apparent public-chain deposit can leave an equity gap on an appchain or off-chain ledger; state the gap explicitly.

## Fee and simulation limits

25. Check current accepted transaction versions and fee token rules from official Starknet documentation. For current v3 flows, model STRK fee balance, nonce, resource bounds, and account-specific validation requirements as separate readiness questions.
26. An unsigned simulation that skips validation can estimate some execution behavior but gives only narrow evidence about whether the controlled account could authorize and pay for a real transaction. Label the skipped checks.
27. A read-only audit should not claim claimability from a successful view call alone. Verify relevant permissions, deadline, nonce, fee path, account implementation, and withdrawal liquidity without signing or broadcasting.
28. Cross-check material balances or claims through an independent RPC, verified explorer, or protocol source at comparable finalized blocks. Preserve conflicting observations instead of averaging them.
29. Finish each protocol family as verified positive, verified zero within a named method and block, or unknown. State coverage of contracts, events, pages, decoders, and unavailable private/appchain state.

## Completion checks by evidence type

- **Namespace:** Chain ID, final block, and exact wallet/account-contract address are confirmed.
- **Control:** Deployment state, class hash, signer or guardian path, and exact address derivation are established.
- **Transactions:** Accepted `DEPLOY_ACCOUNT`, `DECLARE`, and `INVOKE` history is reconciled with nonce where possible.
- **Receipts:** Execution and finality status are read for each event or state transition used as evidence.
- **Parsers:** Failed and unsupported transaction or event decodes are counted and retained as gaps.
- **Tokens:** Candidate contracts include receipt-derived assets, not only a wallet or indexer catalog.
- **ABIs:** Proxy implementation and the correct call names, arguments, and return types are verified at the block.
- **NFTs:** Current owner and position state are checked separately from mint, transfer, or burn history.
- **Orders:** Catch-up pages are complete; live, filled, cancelled, expired, and reverted states are distinguished.
- **Storage:** Any direct slot read has a source-verified formula for the deployed class and independent review.
- **Staking:** Pool enumeration, reward authority, accrued rewards, and pending exits are covered.
- **Vaults:** Share NAV, backing, debt, withdrawal liquidity, and frozen status are reported distinctly.
- **Claims:** Merkle root, proof, claim state, and expiry are verified or the proof gap is recorded.
- **Appchains:** Address mapping and external equity are reconciled or explicitly left unresolved.
- **Execution:** Current fee token, account nonce, validation path, and simulation limits are documented.
- **Cross-check:** Material claims have a second provider or primary protocol source at a comparable block.

For each candidate, retain an evidence row with `chain ID`, `block hash`, `wallet`, `contract`, `class hash`, `method or event`, `raw result`, `unit`, `authority`, `status`, and `source`. Keep token balances, vault shares, collateral, and claim receipts linked so one economic position is not counted several times. Use raw integer values until decimals and conversion formulas are verified.

If an indexer or RPC omits older events, record the last complete block, continuation token, page count, and affected contracts. Query a suitable archival source if available. A complete event scan still does not prove complete account activity when a protocol stores state without emitting the event expected by the parser.

For upgraded contracts, retain the implementation or class hash that applied at the read block and at historically relevant transactions. Never apply a current ABI or storage formula blindly to old receipts. If source, ABI, or class history cannot be reconciled, label the derived amount unknown.

When an apparent claim depends on a bridge or off-chain executor, verify both sides of the lifecycle and its current status. A source-chain deposit event alone does not prove destination-chain credit, and a destination withdrawal request alone does not prove finalized release. Keep the unresolved leg as a separate coverage item.

State a possible recovery sequence only as read-only feasibility: exact controlled account, required signer policy, current nonce and fee token, contract permissions, pending exit or message, and liquidity. Do not infer that a successful `call` or unsigned simulation guarantees a signed transaction will pass validation or remain executable.

## Source anchors to revisit

- [Starknet RPC OpenRPC specification](https://github.com/starkware-libs/starknet-specs/blob/master/api/starknet_api_openrpc.json) for chain, block, class, storage, event, nonce, transaction, and receipt semantics.
- [Starknet documentation](https://docs.starknet.io/) for account contracts, address derivation, execution, and current network behavior.
- [Starknet transaction-version guidance](https://www.starknet.io/developers/roadmap/v3-transactions/) and current release documentation for fee and validation rules.
- Current official source and verified deployed class for every protocol reviewed; record source revision and block. This guide does not certify any protocol's storage formula or withdrawal policy.
