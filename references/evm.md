# EVM discovery and evidence guide

Use this reference for read-only discovery across EVM chains after the user supplies fresh addresses.
Treat an address as an investigation seed, not proof that every related contract or destination belongs to the user.
Keep chain, block, timestamp, contract, token, and position identities separate throughout the audit.

## Establish the chain and data boundary

1. Build a candidate-chain set from user statements, wallet network settings the user supplied, signed transaction history, inbound transfers, bridge receipts, and protocol events.
2. Add plausible long-tail chains through current chain registries, wallet support lists, protocol deployment registries, bridge route lists, and explorer links; do not rely on a fixed popular-chain list.
3. Verify each candidate's current chain ID, network status, native asset, explorer, and RPC from its official documentation or maintained registry before querying.
4. Record the runtime date, chain ID, RPC/provider, explorer/indexer, head block and timestamp, and finalized or safe block when available.
5. Reject a provider whose `eth_chainId` conflicts with the intended chain; label stale or unsynced heads, archival limits, indexing lag, and unavailable history.
6. Distinguish mainnets, testnets, appchains, forks, and superseded networks; the same hexadecimal address does not imply the same asset or owner on each.
7. Pin read-only state calls to a stated block where feasible; record when a dashboard and RPC were sampled at different times.

## Discover activity without mistaking nonce for completeness

8. Query native balance, `eth_getCode`, and `eth_getTransactionCount` at the chosen block; nonce counts sent transactions only.
9. Search signed transactions, internal/native transfers, token transfer logs, approvals, NFTs, and protocol events using indexed history and independent explorer or RPC checks.
10. Search inbound activity and contract-created positions even when the address has no outgoing transactions or native gas balance.
11. Paginate every history endpoint to exhaustion; record page/cursor coverage, block span, item count, filters, and provider result caps.
12. Split oversized `eth_getLogs` requests into bounded block windows and deduplicate by chain, transaction hash, log index, and block hash.
13. Reconcile indexer results against transaction receipts and current contract state; reorged or removed logs must not remain live evidence.
14. Where history is pruned or an API fails, write the missing block range and affected search class explicitly; never interpret an empty response as zero holdings.
15. Search both direct address topics and protocol-specific indexed fields; beneficiary, owner, depositor, recipient, and referral may occupy different fields.
16. Decode calldata and events only after verifying the emitting contract and ABI; a generic token transfer can be a deposit, mint, fee, refund, or unrelated flow.
17. Follow approvals as discovery clues, not assets; an allowance alone does not prove an open position or a recoverable balance.

## Identify contracts and historical protocols

18. Start from transactions, receipts, event emitters, minted receipt tokens, and official deployment registries; history-derived candidates outrank dashboard suggestions.
19. For each candidate, record chain ID, contract address, deployment/version, implementation address if proxied, code hash, ABI source, and evidence links.
20. Confirm bytecode with `eth_getCode`; for proxies inspect implementation or beacon slots, upgrades, and the implementation active at the relevant historical block.
21. Prefer verified source and ABI from official repositories or explorers, then corroborate selectors/events against actual receipts and code.
22. Unverified, clone, migrated, deprecated, or abandoned contracts require a lower confidence label and an explicit statement of what cannot be decoded.
23. Trace factory-created vaults, strategy contracts, position managers, staking wrappers, migration contracts, and escrow contracts only when anchored to the user's history.
24. Check protocol migrations and successor claims without assuming old shares or rights automatically moved to the new deployment.
25. Separate custody contracts, accounting contracts, reward distributors, gauges, and governance lock contracts; one protocol may expose several independent rights.

## Read state that dashboards can miss

26. Enumerate direct balances by token contract and chain, including native, wrapped, rebasing, yield-bearing, and NFT position tokens.
27. Query position-specific views at a pinned block: owner/beneficiary, shares, deposits, staked amounts, pending rewards, unlock time, claim status, and withdrawn amounts.
28. Look for LP positions, uncollected trading fees, removed liquidity proceeds, lending collateral, borrow liabilities, vault shares, vesting, lockups, escrows, refunds, and recovery claims.
29. Inspect tokenized and non-tokenized positions: ERC-20 receipt tokens, ERC-721/1155 positions, mappings keyed by user, and event-derived IDs.
30. Use history to derive position IDs, pool keys, gauges, maturities, and beneficiary addresses; generic `balanceOf` is insufficient for many protocols.
31. For AMMs, inspect fee growth or `collect`-style views, pool reserves/liquidity, and position ranges; a zero wallet LP-token balance does not rule out NFT liquidity.
32. For lending and margin, report supplied assets alongside debts, liquidation state, caps, and withdrawal constraints; do not call gross collateral recoverable value.
33. For rewards, distinguish accrued, claimable, vested, forfeited, and already claimed amounts.
34. For vesting and escrow, verify who may claim, the schedule, cliff, revocation, expiration, and whether a claim was already consumed.
35. For lost-token recovery features, identify the actual authorized claimant and eligible token/contract; a generic rescue function is not a user right.
36. When a protocol tracks frozen or stale shares, compare ledger shares, conversion rate, redeemability, vault liquidity, and actual underlying backing.
37. A view returning nominal assets does not prove the pool can pay them; inspect reserves, queues, insolvency, pauses, withdrawal limits, and current contract behavior.
38. Use unsigned `eth_call` or local read-only simulation for a full-size redemption/withdrawal quote when supported; capture block and call parameters.
39. Check slippage, fees, debt repayment, cooldowns, epoch limits, and route-specific liquidity; a tiny test quote cannot establish full-position proceeds.
40. If a quote reverts, decode the error where possible and report the revert plus unknown recoverability, rather than treating it as zero.
41. Identify duplicate economic claims: a vault share and its underlying deposit, a staked LP and its pool reserves, or bridged representation and locked origin collateral.
42. Value each independent economic position once; show gross exposure and enforce claim collisions before adding a recoverable total.

## Evidence and stopping rules

43. For every candidate, retain the discovery path, exact contract and position identifiers, source URLs, block/time, call or event, decoded fields, and confidence.
44. Distinguish observed on-chain state, protocol documentation, simulator output, and inference; label each separately.
45. Negative findings require defined coverage: chains searched, address roles, history range, pagination completion, state calls, and source freshness.
46. Retry transient rate limits, timeouts, and inconsistent heads with bounded backoff and an independent provider or explorer when useful.
47. Stop after the retry budget or a stable provider limitation; preserve partial results and name the unresolved chain, range, or protocol.
48. Never sign, broadcast, submit claims, spend gas, change approvals, or set up persistent monitoring, tracking, or telemetry in this audit.
49. Unsigned read calls and simulations are allowed; actual financial execution belongs to a separate user-owned scope.

## Candidate decision record

50. Keep one row per chain, protocol, contract, and position ID; avoid collapsing distinct vaults or epochs under one token symbol.
51. Record `observed balance`, `claimable now`, `conditional right`, `historical/closed`, or `unknown`, with the method that supports the label.
52. Attach a current quote only to the exact position size and call path tested; state quote expiration and block sensitivity.
53. Recheck decimals, share scaling, rebases, and wrapper exchange rates from the verified contracts before converting units.
54. Preserve liabilities and encumbrances in the same row as the associated collateral or claim.
55. If an authorized caller differs from the supplied address, do not suggest the supplied address can exercise the right.
56. Mark a candidate exhausted only after history, current state, protocol-specific IDs, and any migration route have been checked.
57. For ambiguous contracts, leave the candidate open with a concrete next read-only check, not a speculative balance.
58. Record searches that produced no candidate so coverage can be reviewed without implying every unknown protocol was surveyed.
59. Keep all output local to this audit session unless the user separately requests an export; do not install watchers or background jobs.

## Source anchors to verify at audit time

- [Ethereum JSON-RPC methods](https://ethereum.org/developers/docs/apis/json-rpc/) define chain/state/history calls and block tags; verify chain-specific RPC behavior and provider limits.
- [OpenZeppelin proxy documentation](https://docs.openzeppelin.com/contracts/5.x/api/proxy) explains implementation and beacon patterns; verify the target's actual proxy design and upgrade history.
- [EIP-1967](https://eips.ethereum.org/EIPS/eip-1967) specifies common proxy slots; do not assume all proxies use it.
- [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [ERC-721](https://eips.ethereum.org/EIPS/eip-721), and [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) define common transfer/ownership interfaces, not protocol position completeness.
- Consult current official protocol deployment registries, verified contract source, and chain documentation for every investigated protocol and network; do not carry forward an old contract list.
