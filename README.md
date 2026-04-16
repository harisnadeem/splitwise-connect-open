# splitwise-connect-open

A public, sanitized Splitwise skill and CLI for Zo Computer.

It supports both personal API key auth and OAuth2, covers the full documented Splitwise API surface, and includes raw passthrough helpers for endpoints or payloads that may evolve over time.

## What this repo is for

Use this repo if you want a one-stop Splitwise integration that can:

- verify your Splitwise connection
- read users, friends, groups, expenses, comments, notifications, currencies, and categories
- create and update groups, friends, expenses, and comments
- delete and restore supported resources
- handle OAuth token persistence and refresh
- stay reliable behind Cloudflare by using `cloudscraper`

This repo is designed to be safe to publish:

- no personal names, emails, IDs, balances, or friend lists
- no committed tokens or auth session files
- no hardcoded secrets
- examples use placeholders only

## Repository layout

- `SKILL.md`: Zo skill entrypoint and quick-start instructions
- `scripts/splitwise_connect.py`: main CLI
- `scripts/requirements.txt`: Python dependency list
- `references/api-coverage.md`: endpoint coverage map
- `docs/AUTHENTICATION.md`: API key and OAuth setup
- `docs/COMMANDS.md`: detailed command guide
- `docs/RELEASE.md`: public release checklist
- `docs/PRIVACY.md`: sanitization and publishing notes
- `examples/`: example JSON payloads for common operations

## Features

### Authentication

- API key auth via `SPLITWISE_API_KEY`
- OAuth2 authorization code flow
- token refresh
- configurable token and auth-session file locations

### Splitwise API coverage

- Users
- Groups
- Friends
- Expenses
- Comments
- Notifications
- Supported currencies
- Supported categories
- Raw `api-get` and `api-post` helpers

## Requirements

- Python 3.10+
- a Splitwise app created at `https://secure.splitwise.com/apps`
- one of:
  - personal API key
  - OAuth client ID and client secret

## Installation

### Option 1: local virtual environment

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
```

### Option 2: existing Python environment

```bash
pip install -r scripts/requirements.txt
```

## Quick start

### 1. Check the CLI help

```bash
python3 scripts/splitwise_connect.py --help
```

### 2. Authenticate

For API key auth:

```bash
export SPLITWISE_API_KEY="your_api_key_here"
python3 scripts/splitwise_connect.py check-auth
```

For OAuth2:

```bash
python3 scripts/splitwise_connect.py auth-url \
  --client-id "your_client_id" \
  --redirect-uri "https://example.com/callback"
```

Open the printed URL, approve the app, then exchange the callback URL:

```bash
python3 scripts/splitwise_connect.py exchange-callback \
  --client-id "your_client_id" \
  --client-secret "your_client_secret" \
  --callback-url "https://example.com/callback?code=...&state=..."
```

### 3. Run commands

```bash
python3 scripts/splitwise_connect.py list-friends
python3 scripts/splitwise_connect.py list-groups
python3 scripts/splitwise_connect.py list-expenses --limit 10
```

## Common examples

### Create a friend

```bash
python3 scripts/splitwise_connect.py create-friend \
  --user-email "person@example.com" \
  --user-first-name "First" \
  --user-last-name "Last"
```

### Create an expense

```bash
python3 scripts/splitwise_connect.py create-expense \
  --cost 1200 \
  --description "Groceries" \
  --currency-code PKR \
  --share "user_id=111,paid_share=1200,owed_share=600" \
  --share "user_id=222,paid_share=0,owed_share=600"
```

### Create a group

```bash
python3 scripts/splitwise_connect.py create-group \
  --name "Apartment 2026" \
  --group-type home \
  --member "email=alex@example.com,first_name=Alex,last_name=Example" \
  --member "user_id=5823"
```

### Raw POST helper

```bash
python3 scripts/splitwise_connect.py api-post \
  --path /create_comment \
  --body-file examples/create-comment.json
```

## Documentation

- Authentication guide: `docs/AUTHENTICATION.md`
- Command reference: `docs/COMMANDS.md`
- Privacy and sanitization notes: `docs/PRIVACY.md`
- Release checklist: `docs/RELEASE.md`

## Notes on Cloudflare

Splitwise sits behind Cloudflare. In practice, plain `urllib` or `requests` flows can intermittently fail even with valid credentials. This CLI uses `cloudscraper` to keep the integration usable in real environments.

## License

MIT. See `LICENSE`.
