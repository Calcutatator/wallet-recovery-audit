# Install Wallet Recovery Audit

This package contains a reusable agent skill for deep, read-only EVM, Solana and Starknet wallet recovery research. It contains no previous user's wallet list, balances, holdings, transactions or audit reports.

## With Codex

Clone the public repository into your local skills directory:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/Calcutatator/wallet-recovery-audit.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/wallet-recovery-audit"
```

Alternatively, download the repository using GitHub's **Code → Download ZIP**, attach the archive in a new task and ask:

> Install this wallet-recovery-audit skill in my local skills directory. Inspect the package first. Do not overwrite an existing skill without checking it. Then use the skill to collect my public EVM, Solana and Starknet addresses and perform a read-only audit.

For manual installation, unzip the archive, rename the extracted folder to `wallet-recovery-audit` if needed, and place it in `${CODEX_HOME}/skills` if `CODEX_HOME` is configured, otherwise `~/.codex/skills`. The final file should be `skills/wallet-recovery-audit/SKILL.md`, not a doubly nested folder. If an installed copy already exists, compare it before replacing it. Start a new task if the current task's skill list has not refreshed.

Invoke it with:

```text
Use $wallet-recovery-audit. Ask me for my EVM, Solana and Starknet public addresses, then investigate overlooked contract positions, rewards, rent and bridge settlements in depth. Give me the combined report, coverage gaps and practical claim instructions, with every wallet address written in full.
```

Other agents that support `SKILL.md` folders can use their documented skill-import mechanism. The workflow does not depend on Codex-specific research tools; it adapts to the host's available browsing, RPC, execution and delegation capabilities.

## What happens after installation

The agent asks for EVM addresses, Solana addresses and Starknet addresses. Each group can be skipped explicitly with “none.” It validates formats, investigates current state and historical activity, follows less common protocols and bridge destinations, tests exits with unsigned simulations where available, and produces a consolidated report plus CSV ledgers with full addresses.

Reports distinguish current claims, managed positions, ordinary holdings, future or unpriced rights, known losses, settled bridges and evidence gaps. A failed endpoint is never counted as a zero balance. The skill cannot guarantee discovery across every chain or every private/off-chain entitlement.

When asked how to claim a finding, the agent verifies the current interface and gives the exact sending account, network, function, inputs, expected receipts and fee information. You review and submit the transaction in your own wallet. The audit itself does not connect a wallet, request keys, sign, broadcast, trade or create tracking jobs.

## Requirements and privacy

- Live research needs internet access, a browser or HTTP/RPC tools, and usable public providers. Some history or proofs may require an explicitly configured provider; unavailable access stays visible as a gap. No paid provider is bundled or required to install.
- Python 3.10 or later is needed only for the optional local helper. It uses the standard library, has no network calls and is not a standalone blockchain scanner.
- Audit artifacts stay in a private local run directory outside the skill. Necessary public identifiers are queried with the chosen explorers, RPC nodes and protocol APIs; this is not an offline anonymity guarantee.
- No telemetry, creator endpoint, wallet database, recurring monitoring or cross-user memory is included. Do not share your private audit run together with the reusable skill.
- Addresses and runtime observations never belong in the reusable package. Share only the original skill archive or a reviewed, generic update.
