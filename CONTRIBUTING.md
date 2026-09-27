# Contributing

Contributions should improve generic discovery, evidence, recovery guidance or the offline helper.

- Use synthetic identifiers and observations. Do not submit real wallet lists, balances, transaction history, audit reports, screenshots, credentials, private paths or personal contact details in code, issues, pull requests or logs.
- Keep audit inputs and outputs outside this repository. `.gitignore` is an extra precaution, not a privacy guarantee; review the staged files and diff before committing.
- Prefer current first-party documentation. Describe provider limitations and the evidence required for a conclusion.
- Keep the helper offline and dependency-free. Do not add telemetry, wallet collection endpoints, signing or transaction submission.
- Test meaningful behavioral changes with synthetic fixtures, and explain the validation performed.

Run the offline tests before submitting:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_*.py'
```

If a bug needs real chain data to reproduce, first reduce it to a synthetic example or a description that does not reveal someone's wallet activity. Never paste secrets into an issue.
