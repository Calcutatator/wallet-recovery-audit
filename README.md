# Wallet Recovery Audit

An agent skill for deep, read-only research into overlooked funds across **EVM, Solana and Starknet** wallets.

It collects public addresses, follows historical activity into niche networks and protocols, reconciles bridges, and explains practical recovery routes. It distinguishes recorded balances from assets with backing and a usable exit.

## Install with an agent

Copy this into Codex or another agent that can install local skills:

```text
Install the Wallet Recovery Audit skill from:
https://github.com/Calcutatator/wallet-recovery-audit

Inspect the repository first. In Codex, install it as
${CODEX_HOME}/skills/wallet-recovery-audit if CODEX_HOME is set,
otherwise ~/.codex/skills/wallet-recovery-audit.
For another host, use its documented SKILL.md installation location.
If a copy already exists, compare it and preserve local changes.
Read SKILL.md, then use the skill to guide me through the EVM,
Solana and Starknet public-address intake and a read-only audit.
Keep my addresses and audit outputs outside the installed skill.
```

If the host needs to refresh its skill list, open a new task after installation and use the run prompt below.

## Manual installation in Codex

In Codex, clone this repository into your local skills directory:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/Calcutatator/wallet-recovery-audit.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/wallet-recovery-audit"
```

If the destination already contains files, the clone command stops; compare that copy before updating it. Alternatively, use GitHub's **Code → Download ZIP** and follow [INSTALL.md](INSTALL.md).

## Run the audit

Start a new task in your agent and paste:

```text
Use $wallet-recovery-audit. Ask me for my EVM, Solana and Starknet
public addresses in order, letting me skip any group with "none".
Run the deep read-only audit, follow niche protocols and bridges,
and produce the combined report and CSV ledgers with full copyable
addresses, evidence, coverage gaps and practical recovery steps.
```

Reply to the address prompts with public addresses, one per line. You do not need to connect a wallet or run the Python helper yourself. For a finding you want to recover, ask: “Show me how to recover this finding using my full sending address.”

Live research requires the agent to have browsing or HTTP/RPC access. Missing providers or historical data must be reported as gaps. Python 3.10+ is optional and only needed for the local helper; installing the skill alone does not execute a blockchain scan.

For other hosts, invoke the skill using that host's mechanism or ask the agent to read the installed `SKILL.md` and follow it. A longer [starter prompt](START-PROMPT.md) is also available.

### Instructions for agents executing the skill

1. Load [SKILL.md](SKILL.md) as the entry point, then [evidence and outputs](references/evidence-and-output.md) and the applicable chain/bridge guides it links to.
2. Collect the three address groups in order. Treat only an explicit “none” as a skipped group; do not search unrelated files or memory for wallets.
3. Keep input, evidence and reports in a private run directory outside this repository. If using the offline helper, follow [data-format.md](references/data-format.md); it validates and exports data, but does not perform the research.
4. Use available read-only tools to investigate, document coverage and verify findings. Follow the skill's stopping conditions and claim handoff rules, then return the combined report and linked artifacts. Never sign, broadcast or move funds.

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
