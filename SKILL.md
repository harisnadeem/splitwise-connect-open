---
name: splitwise-connect-open
description: Comprehensive Splitwise skill for API key or OAuth2 auth, full endpoint coverage, and generic helpers for account, friends, groups, expenses, comments, notifications, currencies, and categories.
compatibility: Works in any agent or terminal environment that supports Python and environment variables.
---

# Splitwise Connect Open

Use this skill when you want one place to work with Splitwise from chat or from the terminal.

## What this skill covers

This CLI maps to every documented Splitwise API area:

- Users
  - `check-auth`
  - `get-current-user`
  - `get-user`
  - `update-user`
- Groups
  - `list-groups`
  - `get-group`
  - `create-group`
  - `delete-group`
  - `undelete-group`
  - `add-user-to-group`
  - `remove-user-from-group`
- Friends
  - `list-friends`
  - `get-friend`
  - `create-friend`
  - `create-friends`
  - `delete-friend`
- Expenses
  - `list-expenses`
  - `get-expense`
  - `create-expense`
  - `update-expense`
  - `delete-expense`
  - `undelete-expense`
- Comments
  - `get-comments`
  - `create-comment`
  - `delete-comment`
- Notifications
  - `get-notifications`
- Reference data
  - `list-currencies`
  - `list-categories`
- Generic passthrough helpers
  - `api-get`
  - `api-post`

It also includes the OAuth2 flow:

- `auth-url`
- `exchange-code`
- `exchange-callback`
- `refresh`

## Why `cloudscraper` is used

Splitwise is fronted by Cloudflare. In practice, standard Python HTTP clients can get challenged or blocked even when the request itself is otherwise correct. This skill uses `cloudscraper` for API calls so it stays reliable in real use.

## Files

- `scripts/splitwise_connect.py`
- `scripts/requirements.txt`
- `.gitignore`
- Token file default: repository-local `splitwise_token.json`
- Auth session default: repository-local `splitwise_auth_session.json`

## Setup

Create a Splitwise app at `https://secure.splitwise.com/apps`.

Then choose one auth mode.

### Option A: Personal API key

Set this environment variable:

- `SPLITWISE_API_KEY`

### Option B: OAuth2

Set these environment variables:

- `SPLITWISE_OAUTH_CLIENT_ID`
- `SPLITWISE_OAUTH_CLIENT_SECRET`

## Install dependency

```bash
pip install -r scripts/requirements.txt
```

If your Python environment blocks global installs, use a virtual environment instead:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
```

## Core usage

Show help:

```bash
python3 scripts/splitwise_connect.py --help
```

Check auth:

```bash
python3 scripts/splitwise_connect.py check-auth
```

Force JSON output:

```bash
python3 scripts/splitwise_connect.py --json get-current-user
```

## OAuth examples

Generate auth URL:

```bash
python3 scripts/splitwise_connect.py auth-url \
  --redirect-uri "https://example.com/callback"
```

Exchange full callback URL:

```bash
python3 scripts/splitwise_connect.py exchange-callback \
  --callback-url "https://example.com/callback?code=...&state=..."
```

Refresh stored token:

```bash
python3 scripts/splitwise_connect.py refresh
```

## Command reference

### Users

Current user:

```bash
python3 scripts/splitwise_connect.py get-current-user
```

Another user:

```bash
python3 scripts/splitwise_connect.py get-user --id 12345
```

Update a user:

```bash
python3 scripts/splitwise_connect.py update-user \
  --id 12345 \
  --first-name "Ada" \
  --last-name "Lovelace" \
  --default-currency USD
```

Or with JSON:

```bash
python3 scripts/splitwise_connect.py update-user \
  --id 12345 \
  --body-json '{"locale":"en","default_currency":"EUR"}'
```

### Groups

List groups:

```bash
python3 scripts/splitwise_connect.py list-groups
```

Get a group:

```bash
python3 scripts/splitwise_connect.py get-group --id 321
```

Create a group:

```bash
python3 scripts/splitwise_connect.py create-group \
  --name "Apartment 2026" \
  --group-type home \
  --simplify-by-default \
  --member "email=grace@example.com,first_name=Grace,last_name=Hopper" \
  --member "user_id=5823"
```

Delete and restore:

```bash
python3 scripts/splitwise_connect.py delete-group --id 321
python3 scripts/splitwise_connect.py undelete-group --id 321
```

Add or remove users:

```bash
python3 scripts/splitwise_connect.py add-user-to-group \
  --group-id 321 \
  --user-id 5823

python3 scripts/splitwise_connect.py remove-user-from-group \
  --group-id 321 \
  --user-id 5823
```

### Friends

List friends:

```bash
python3 scripts/splitwise_connect.py list-friends
```

Get one friend:

```bash
python3 scripts/splitwise_connect.py get-friend --id 5823
```

Create a single friend:

```bash
python3 scripts/splitwise_connect.py create-friend \
  --user-email "ada@example.com" \
  --user-first-name "Ada" \
  --user-last-name "Lovelace"
```

Create multiple friends:

```bash
python3 scripts/splitwise_connect.py create-friends \
  --friend "email=alan@example.org,first_name=Alan,last_name=Turing" \
  --friend "email=existing@example.org"
```

Delete a friendship:

```bash
python3 scripts/splitwise_connect.py delete-friend --id 5823
```

### Expenses

List expenses:

```bash
python3 scripts/splitwise_connect.py list-expenses --limit 20
```

Filter by friend, group, or time:

```bash
python3 scripts/splitwise_connect.py list-expenses \
  --friend-id 5823 \
  --dated-after "2026-01-01T00:00:00Z" \
  --limit 50
```

Get one expense:

```bash
python3 scripts/splitwise_connect.py get-expense --id 51023
```

Create an expense with explicit shares:

```bash
python3 scripts/splitwise_connect.py create-expense \
  --cost 25.00 \
  --description "Lunch" \
  --currency-code USD \
  --share "user_id=1001,paid_share=25.00,owed_share=0" \
  --share "user_id=1002,paid_share=0,owed_share=25.00"
```

Create an equal group split:

```bash
python3 scripts/splitwise_connect.py create-expense \
  --group-id 321 \
  --split-equally \
  --cost 120 \
  --description "Internet bill" \
  --currency-code USD
```

Create with raw JSON:

```bash
python3 scripts/splitwise_connect.py create-expense \
  --body-json '{
    "cost":"79.50",
    "description":"Groceries",
    "currency_code":"USD",
    "users__0__user_id":"1001",
    "users__0__paid_share":"79.50",
    "users__0__owed_share":"0",
    "users__1__user_id":"1002",
    "users__1__paid_share":"0",
    "users__1__owed_share":"79.50"
  }'
```

Update an expense:

```bash
python3 scripts/splitwise_connect.py update-expense \
  --id 51023 \
  --description "Groceries and snacks" \
  --details "Added drinks too"
```

Or overwrite shares on update:

```bash
python3 scripts/splitwise_connect.py update-expense \
  --id 51023 \
  --share "user_id=1001,paid_share=60,owed_share=20" \
  --share "user_id=1002,paid_share=0,owed_share=40"
```

Delete and restore:

```bash
python3 scripts/splitwise_connect.py delete-expense --id 51023
python3 scripts/splitwise_connect.py undelete-expense --id 51023
```

### Comments

List comments:

```bash
python3 scripts/splitwise_connect.py get-comments --expense-id 51023
```

Create a comment:

```bash
python3 scripts/splitwise_connect.py create-comment \
  --expense-id 51023 \
  --content "Does this include delivery?"
```

Delete a comment:

```bash
python3 scripts/splitwise_connect.py delete-comment --id 79800950
```

### Notifications

Get notifications:

```bash
python3 scripts/splitwise_connect.py get-notifications --limit 25
```

Get only recent notifications:

```bash
python3 scripts/splitwise_connect.py get-notifications \
  --updated-after "2026-01-01T00:00:00Z"
```

### Currencies and categories

Supported currencies:

```bash
python3 scripts/splitwise_connect.py list-currencies
```

Supported categories:

```bash
python3 scripts/splitwise_connect.py list-categories
```

## Raw helpers

These are useful when Splitwise adds a field or endpoint and you do not want to wait for a wrapper update.

Raw GET:

```bash
python3 scripts/splitwise_connect.py api-get \
  --path /get_expenses \
  --body-json '{"limit":10,"offset":0}'
```

Raw POST as form data:

```bash
python3 scripts/splitwise_connect.py api-post \
  --path /create_comment \
  --body-json '{"expense_id":51023,"content":"Looks good"}'
```

Raw POST as JSON:

```bash
python3 scripts/splitwise_connect.py api-post \
  --path /create_friend \
  --content-type json \
  --body-json '{"user_email":"ada@example.com","user_first_name":"Ada","user_last_name":"Lovelace"}'
```

## Notes on expense payloads

- `create-expense` and `update-expense` support both:
  - equal split in a group
  - explicit shares with flattened `users__{index}__{property}` fields
- Replacing any share field during `update-expense` overwrites the full share set for that expense
- `category_id` must be a subcategory ID, not a parent category
- Use `list-categories` first if you need a valid category

## Safety notes for open-source use

- Never commit `splitwise_token.json`
- Never commit `splitwise_auth_session.json`
- Never hardcode `SPLITWISE_API_KEY`
- Keep example payloads generic
- Review output before sharing screenshots or logs, because API responses can include names, emails, balances, and other private data

## Troubleshooting

- `401 Invalid API key or OAuth access token`
  - Check the secret value
  - Remove accidental leading or trailing whitespace
  - Regenerate the key if needed
- `403` from Cloudflare or HTML challenge pages
  - Make sure `cloudscraper` is installed
  - Use this script instead of a plain `requests` or `urllib` snippet
- `errors` returned with HTTP 200
  - Splitwise uses `errors` in the response body for many failed writes
  - This script treats non-empty `errors` as failures for write operations
- Expense share issues
  - Each provided share should have both `paid_share` and `owed_share`
  - Use strings for decimal amounts if you are supplying raw JSON
