# Bridge and cross-chain reconciliation guide

Use this reference for read-only matching of a user's origin-chain activity to destination receipt, refund, or pending right.
Begin with addresses freshly supplied for the audit; do not import prior wallet identities or assume every destination is controlled by the origin signer.
Apply the same method to EVM, Solana, Starknet, and mixed-chain routes, with chain-specific address and account models.

## Identify the route and message

1. Derive bridge candidates from origin transaction receipts, log emitters, calldata, token transfers, official route/deployment registries, and historical UI links.
2. Include canonical rollup bridges, liquidity networks, burn/mint rails, intent/relayer routes, messaging layers, and app-specific bridges; long-tail routes come from evidence, not a static name list.
3. Verify current chain IDs or domain IDs, bridge contract/program IDs, versions, supported route, and source documentation before decoding.
4. Record origin chain and transaction, block/time/finality, sender, actual debited token and amount, bridge contract, destination chain, recipient, output token, quoted output, fees, and deadlines.
5. Separate the user's signed transaction from emitted bridge messages: one transaction may emit multiple deposits, messages, or token movements.
6. Use the protocol's exact identity when available: deposit ID, message hash, nonce, sequence plus emitter, withdrawal hash, ticket ID, transfer ID, or proof leaf.
7. Scope an ID by protocol version, origin chain/domain, emitter or contract, and destination where required; a bare numeric deposit ID may collide.
8. Capture log index and payload hash for duplicate or amended messages, speed-ups, partial fills, and replay checks.
9. Verify bridge contract identity through code, proxy implementation, official deployments, and ABI as of the historical event.
10. If exact identifiers are unavailable, match on origin/destination chains, recipient, token mapping, amount after fees, and bounded time window; mark this weaker evidence.
11. Never equate a similar amount or timestamp with a confirmed transfer when multiple candidates or route changes fit.

## Follow the full lifecycle

12. On the origin, distinguish approval, swap, bridge deposit, burn, lock, message emission, proof posting, cancellation, and refund.
13. On the destination, distinguish message availability, execution attempt, successful token credit, escrow/contract credit, claimable receipt, and final recipient ownership.
14. A consumed message proves a protocol action was processed; inspect its effect before claiming the user received liquid assets or equity.
15. A destination transfer to a router, pool, custodian, smart account, or alternate beneficiary is not a wallet receipt without ownership evidence.
16. Decode destination transaction receipts, emitted token events, account state, and bridge status from independent sources where possible.
17. For relayer or intent systems, separate user delivery from relayer repayment and pool settlement; a later refund event may pay the relayer.
18. Inspect partial fills, slow fills, retries, route amendments, failed execution, expiry, reclaims, refunds, and any residual amount.
19. Match origin amount to destination amount after decimals, token mapping, bridge fee, relayer fee, gas drop, swap output, and partial fill; record the equation.
20. Trace intermediate hops and wrapped representations; avoid counting locked origin collateral plus destination token as two independent user assets.
21. Reconcile a burn/mint route with the issuer's message and attestation identifiers, destination mint, and refund or replacement status.
22. For canonical exits, identify the withdrawal initiation, proof, finalization window, finalized execution, and actual recipient credit.
23. For retryable tickets or similar inbox mechanisms, inspect ticket creation, auto-execution, later retries, expiry, and configured refund beneficiaries.
24. For delayed exits, calculate eligibility from current official rules and on-chain state; avoid fixed wait periods copied from old docs.
25. For cancellable or refundable routes, verify the deadline, cancellation window, authorized caller, amount available, and whether it has already been claimed.
26. A pending right is a conditional claim, not a current destination balance; state what action and eligibility are still required.

## Reconnect address models across ecosystems

27. EVM addresses can be reused across EVM chains, but chain-specific contracts, tokens, and account deployment still need separate verification.
28. For Solana, identify the wallet key, token-account owner, mint, token program, and associated token account derivation; a token account address is not itself proof of wallet ownership.
29. Check non-associated token accounts, program-derived accounts, and wrapped-native accounts when the bridge payload or transaction history points to them.
30. For Starknet, identify the account contract and exact L1↔L2 message payload, recipient felt/address encoding, and consumption/finalization state.
31. Do not map a 20-byte EVM address to a Starknet account or a Solana key by visual similarity, truncation, or assumed common seed.
32. Account aliases and deterministic smart accounts require the documented derivation, factory/implementation, deployment state, and control evidence.
33. A destination smart account may be undeployed, controlled by a different signer, or governed by a multisig; the origin signer alone does not establish ownership.
34. When ownership is uncertain, report destination delivery separately from user-accessible recovery; request user proof only if needed for a later scope.

## Produce an evidence-bounded status

35. For each bridge leg, label `origin observed`, `message identified`, `destination executed`, `recipient credited`, `refunded`, `cancelled`, or `unresolved` with evidence for each transition.
36. Give source and destination transaction identifiers, chain IDs, bridge/message IDs, token IDs, recipient, amount, block/time, and source links.
37. State whether the asset is already held, held in escrow, claimable, in a queue, failed, expired, or diverted to a specified recipient.
38. Keep ownership confidence and transfer-status confidence separate; a confirmed destination credit can still have unknown claimant control.
39. When a route changes token or address formats, cite the current official specification or contract behavior used to decode it.
40. Search both protocol indexers and chain receipts; paginate APIs, verify freshness and finality, and check for chain reorganizations.
41. If status services disagree, prefer on-chain receipts and state at a pinned block while recording the discrepancy and indexer lag.
42. Treat an empty API response, missing Solana signature page, unavailable Starknet event range, or explorer outage as a coverage gap.
43. Retry transient failures with bounded backoff, smaller ranges, and an independent official or chain source; stop with unresolved status after the retry budget.
44. Never invent a destination tx from amount/time proximity, treat a message as liquid value, or promise recoverability without access and claim checks.
45. Keep the audit read-only: no signing, broadcasting, claims, on-chain retry or cancellation, approval changes, persistent tracking, or telemetry.
46. Unsigned state calls and local simulations are allowed; any actual financial execution is a separate user-owned decision and scope.

## Match ledger for multi-leg routes

47. Create one row per origin message and one child row per destination execution, partial fill, refund, or onward hop.
48. Preserve the parent message ID when a router swaps or forwards assets through multiple destination transactions.
49. Mark the amount consumed by each child row and compute an unresolved remainder in origin and destination units.
50. Keep protocol fees, token conversion, and relayer repayment outside the user's destination credit total.
51. If a refund returns to a configured alternate address, verify its controller before attributing it to the user.
52. If a destination app issues a receipt token or escrow claim, inspect the receipt's owner and redeemability separately from the bridge delivery.
53. For a bridge that reports `completed`, define whether that means message accepted, contract call executed, or beneficiary credited.
54. Preserve failed attempts and later successful retries so an early revert does not become a false unresolved asset.
55. A proof's availability, submission, and execution are distinct milestones; record the latest observed milestone.
56. Compare claimable or refunded amounts with current pool/escrow backing and pause state where the bridge exposes them.
57. Do not double-count a pending origin refund with a successful destination fill unless protocol rules genuinely permit both.
58. Close a leg only when the exact message is accounted for by destination credit, refund, cancellation, or an explicit terminal protocol state.

## Source anchors to verify at audit time

- [Ethereum JSON-RPC](https://ethereum.org/developers/docs/apis/json-rpc/) defines receipts, logs, state calls, and finality tags used on EVM legs.
- [Wormhole VAA documentation](https://docs.wormhole.com/protocol/infrastructure/vaas/) describes the emitter-chain/emitter/sequence identity; verify the current product and route.
- [Across deposit tracking](https://docs.across.to/introduction/tracking-deposits) distinguishes pending, filled, expired, and refunded deposits; verify current event versions and on-chain state.
- [Arbitrum retryable lifecycle](https://docs.arbitrum.io/how-arbitrum-works/deep-dives/l1-to-l2-messaging) explains ticket creation, redemption, expiry, and refund addresses; verify current chain-specific parameters.
- [Solana token-account documentation](https://solana.com/docs/tokens/basics) distinguishes mint, token account, and owner; verify the actual token program and account authority.
- [StarkGate contracts](https://github.com/starknet-io/starkgate-contracts) and the [current interface](https://starkgate.starknet.io/) are starting points for deployment and lifecycle verification; match deployed versions before interpreting messages or cancellation rights.
- Consult current official canonical rollup exit, issuer attestation, and bridge deployment docs for the investigated route; implementations and timing can change.
