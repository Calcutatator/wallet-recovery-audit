# Claim and withdrawal guide after a verified finding

Use this guide only after a claim, withdrawal, refund, or unlock has been verified against current contract or program state. A historical deposit, token balance, indexed label, or failed API lookup alone is not a claim. Keep the user's final financial action under their control. Never request a seed phrase, private key, signature, or gas sent to a third party.

## Establish the exact route

1. Record the chain's canonical identifier, the full claimant wallet address, the full payout recipient address, the exact asset contract or mint, token decimals, raw base-unit amount, and display amount. Distinguish gross entitlement, withdrawable amount, fees, and expected net receipt. Do not infer a token's value from its symbol, nominal balance, purchase price, or a stale quote.
2. Re-read current claim state at a pinned block or slot. Identify the contract/program actually holding or authorizing the right, including proxies and their current implementation, and verify chain, ABI/IDL, role checks, pause state, claim deadline, required proof, and whether the recipient is fixed or configurable. Recheck before presenting a final claim card if state can change.
3. Find the current official project UI from verified project documentation or a contract's verified links. Confirm that its displayed chain, contract/program, function, asset, amount, and connected-wallet address agree with independent on-chain evidence. Verify the payout recipient separately: it may differ from the connected signer. Do not trust a search result, token-name page, lookalike domain, or old UI version as an instruction source.
4. If the official UI is unavailable or incompatible, identify a verified explorer's write interface or a read-only form preview. Show an unsigned call with the exact function/instruction and named, typed arguments. Derive every argument from the current ABI/IDL, contract storage, event, official proof, or documented API; never guess a selector, recipient, index, proof, or amount. A contract upgrade or UI/deployment-version mismatch is a separate diagnosis from insufficient underlying assets.

## Encode and simulate without signing

- **EVM:** Verify chain ID, target contract and proxy implementation, ABI function signature, payable value, token decimals, allowance/approval requirements, and any permit deadline. Encode arguments with an ABI library and independently decode the resulting calldata. Use `eth_call`/trace or a read-only simulation at the current block with the actual claimant as `from`, the correct `to` and `value`, and current nonce where the simulator requires it. Estimate gas and network fee. Only describe an approval when verified as necessary; specify its spender and bounded allowance. Do not recommend a deposit as a prerequisite unless the verified contract path requires it.
- **Starknet:** Verify the account address, network, deployed account class, target implementation, entrypoint selector, Cairo ABI types, and caller/recipient distinction. Construct `u256` as ABI-defined `low` and `high` limbs in the correct argument order; derive market, bet, token, or position indices from ABI and on-chain records rather than an example's constants. Use current `starknet_simulateTransactions` or equivalent unsigned simulation with the actual sender, current account nonce, resource bounds and fee token supported by the account version. Record any skip flags, including skipped validation or fee charging; they limit what the result proves. When possible, enable fee charging while skipping only account/signature validation as needed for an unsigned simulation. Do not obtain a real signature to make a read-only test pass.
- **Solana/SVM:** Verify program ID, instruction discriminator/version and serialized layout, every account meta in order, writable/signer flags, token program variant, mint, destination token account, authority, recent blockhash, and fee payer. Derive address seeds and associated accounts from documented program code or IDL. Build the transaction locally without signatures and run `simulateTransaction` with the actual authority and account list. If signature verification is skipped, state that explicitly; simulation cannot prove signing control. Report rent, priority fee, and any account-creation cost separately from the claim amount.

If simulation fails, preserve the exact error and transaction context. A wrong-sender or unauthorized-caller error first calls for checking the connected wallet and signer-to-claimant mapping; it is not proof that the asset disappeared. Reconfirm the claim state, proof/index, ABI/version, fee funding, and token recipient. Do not turn an unexplained revert into instructions to transfer funds elsewhere. A successful simulation is evidence for the tested state and flags, not a guarantee of future execution or access to the signing key.

## Present the action for user review

Give the user an official UI path when verified, plus an independently checkable explorer/contract path. State precisely which wallet must connect, which account receives the asset, what the UI should show, what network fee or approval may be requested, and a stop condition if any field differs. Optionally prepare a read-only form or unsigned calldata/instruction for inspection. Under this skill, do not connect a wallet, sign, broadcast, swap, withdraw, bridge, or schedule transactions for the user. The user performs the final financial action; a separate request remains subject to the host's execution rules. Never ask the user to send gas to a person's wallet or support address.

After the user reports execution, ask for or read the public transaction signature/hash, verify the receipt and actual asset transfer to the intended recipient, then refresh the remaining claim state and update the audit. Do not mark a claim completed from a UI success toast alone. Do not create recurring monitoring automatically; offer it only when the user requests it.

## Reusable claim card

| Field | Verified value |
|---|---|
| Status and evidence | `{verified claim / simulation-only / blocked; evidence links}` |
| Network and snapshot | `{canonical network, chain ID, block or slot, UTC time}` |
| Claimant / connected wallet | `{full copyable wallet address}` |
| Payout recipient | `{full copyable address; explain if different}` |
| Asset | `{name, full contract or mint address, decimals}` |
| Amount | `{raw base units} = {display units}; {gross/net distinction}` |
| Official UI | `{verified current URL or unavailable}` |
| Contract or program | `{full target address or program ID; implementation/version if relevant}` |
| Function or instruction | `{exact verified name/signature or discriminator}` |
| Typed parameters and accounts | `{name: type = source-derived value; ordered account metas if applicable}` |
| Encoded unsigned payload | `{calldata or instruction bytes; decode cross-check}` |
| Expected effects | `{asset out of contract, asset into recipient, any burn/approval/lock}` |
| Network cost | `{gas/fee/rent estimate and quote time; fee payer}` |
| Simulation | `{endpoint, actual sender, block/slot, flags, result, limitations}` |
| Stop conditions | `{wrong chain, wallet, target, asset, recipient, amount, approval, or unexpected deposit}` |
| Final step | `User reviews and executes; no signature or broadcast performed by the audit` |
