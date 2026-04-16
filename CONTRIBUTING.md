# Contributing

## Goals

This repository is intended to stay:

- easy to use from Zo or a terminal
- aligned with the public Splitwise API
- free of personal account data
- safe to publish

## Before opening a pull request

1. Keep examples generic.
2. Do not commit tokens, callback URLs, or private account exports.
3. Do not add personal names, email addresses, user IDs, balances, screenshots, or copied account responses.
4. Prefer additive docs updates when Splitwise adds fields or endpoints.
5. Validate the CLI locally.

## Local validation

```bash
python3 -m py_compile scripts/splitwise_connect.py
python3 scripts/splitwise_connect.py --help
```

If you have credentials configured, also run:

```bash
python3 scripts/splitwise_connect.py check-auth
```

## Documentation standards

- Keep the root `README.md` practical and quick to scan.
- Put long-form usage details in `docs/`.
- Keep `references/api-coverage.md` aligned with actual command coverage.
- Use placeholders like `person@example.com`, never real addresses.

## Security and privacy

- Never log or print secret values in docs.
- Keep token and auth-session files ignored.
- Treat all captured API responses as sensitive until scrubbed.
