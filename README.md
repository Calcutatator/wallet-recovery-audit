# Wallet Recovery Audit

An agent skill for deep, read-only research into overlooked funds across **EVM, Solana and Starknet** wallets.

It collects public addresses, follows historical activity into niche networks and protocols, reconciles bridges, and explains practical recovery routes. It distinguishes recorded balances from assets with backing and a usable exit.

## Install

In Codex, clone this repository into your local skills directory:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/Calcutatator/wallet-recovery-audit.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/wallet-recovery-audit"
```

Start a new task and ask:

```text
Use $wallet-recovery-audit and guide me through the address intake.
```

Other agents supporting `SKILL.md` can use their documented import mechanism. See [installation and requirements](INSTALL.md) or use the longer [starter prompt](START-PROMPT.md).

## What it does

1. Asks for EVM, Solana and Starknet public addresses in order; each group can be skipped with “none.”
2. Combines current state with historical transactions, receipts and protocol interactions.
3. Investigates staking, lending, vaults, liquidity positions and fees, vesting, rewards, escrows, refunds, withdrawal queues, Solana account rent and protocol-owned positions.
4. Follows bridge transfers through source payments, destination credits, refunds and unresolved messages.
5. Checks authority, backing, restrictions and practical exits, using unsigned simulations where useful.
6. Produces a combined report, ecosystem details, recovery ledger, full address directory, coverage matrix and bridge reconciliation records.

Action items include **full copyable addresses**. Current claims, managed positions, ordinary holdings, contingent rights and historical payments remain separate. Failed or unavailable checks are explicit gaps.

When asked how to recover a finding, the agent checks the live route and explains the sending account, network, contract or program, inputs, expected receipts and fees. The user reviews and submits any transaction themselves.

## Privacy and boundaries

The repository contains generic instructions and synthetic tests. Audit inputs, wallet lists, balances, transactions and reports belong in a separate private run directory. The helper refuses to create runs inside the installed skill.

There is no telemetry, creator reporting, central wallet database, recurring monitoring or cross-user memory. Research uses necessary public identifiers with the explorers, RPC nodes and protocol APIs selected for a run; those providers receive the queries.

The skill does not ask for keys or seed phrases, connect wallets, sign, broadcast, approve spending or move funds. No particular provider, paid service or agent model is required. Discovery depends on available tools and data: it cannot guarantee coverage of every contract, chain or private entitlement.

## Local helper and tests

Python 3.10+ is needed only for the optional helper. It uses the standard library and makes no network calls. It validates addresses, manages a private run directory and exports CSVs; **it is not a standalone blockchain scanner**.

```sh
python3 scripts/audit_workspace.py --help
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_*.py'
```

See [data formats](references/data-format.md) and [evidence and outputs](references/evidence-and-output.md). The [main skill](SKILL.md) links to the individual chain, bridge and claim guides.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Use synthetic data only; never submit wallet lists, audit outputs or credentials.

## License

[MIT](LICENSE).
