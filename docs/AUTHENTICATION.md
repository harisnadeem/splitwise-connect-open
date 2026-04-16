# Authentication

This skill supports two auth modes:

- personal API key
- OAuth2 authorization code flow

## API key mode

This is the simplest option for personal use.

1. Create an app at `https://secure.splitwise.com/apps`
2. Copy the API key
3. Provide it through one of:
   - `SPLITWISE_API_KEY` environment variable
   - `--api-key` flag

Example:

```bash
export SPLITWISE_API_KEY="your_api_key_here"
python3 scripts/splitwise_connect.py check-auth
```

## OAuth2 mode

Use this when you want a standard authorization flow and stored refreshable tokens.

### Step 1: generate an authorization URL

```bash
python3 scripts/splitwise_connect.py auth-url \
  --client-id "your_client_id" \
  --redirect-uri "https://example.com/callback"
```

This writes an auth-session file locally so the callback state can be verified.

### Step 2: approve the app

Open the printed URL in a browser and approve access.

### Step 3: exchange the callback URL

```bash
python3 scripts/splitwise_connect.py exchange-callback \
  --client-id "your_client_id" \
  --client-secret "your_client_secret" \
  --callback-url "https://example.com/callback?code=...&state=..."
```

### Step 4: refresh when needed

```bash
python3 scripts/splitwise_connect.py refresh \
  --client-id "your_client_id" \
  --client-secret "your_client_secret"
```

## Token files

By default the CLI stores:

- `splitwise_token.json`
- `splitwise_auth_session.json`

in the repository root. Both are ignored by Git.

You can override these locations:

```bash
python3 scripts/splitwise_connect.py \
  --token-file /tmp/splitwise_token.json \
  --auth-file /tmp/splitwise_auth.json \
  check-auth
```

## Which mode should you use?

- API key: easiest for personal scripts and direct terminal use
- OAuth2: better if you want standard consent flow and refresh tokens
