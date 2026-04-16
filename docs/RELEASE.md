# Release Checklist

## Before publishing

1. Validate the script:

```bash
python3 -m py_compile scripts/splitwise_connect.py
python3 scripts/splitwise_connect.py --help
```

2. Confirm ignored local files are not tracked:

```bash
git status --ignored --short
```

3. Run a manual scrub for private markers:

```bash
rg -n -i "example|sample|@|splitwise_token|access_token|refresh_token|client_secret|api_key" .
```

4. Inspect the output and make sure any matches are placeholders, code identifiers, or ignored local files only.

5. Re-read:

- `README.md`
- `docs/AUTHENTICATION.md`
- `docs/COMMANDS.md`
- `docs/PRIVACY.md`

## Suggested first release contents

- README
- MIT license
- contributing guide
- security note
- authentication guide
- command reference
- API coverage note
- example payloads

## Suggested GitHub repo description

Comprehensive Splitwise CLI and agent-friendly skill wrapper with API key and OAuth2 auth, full endpoint coverage, and Cloudflare-friendly requests.

## Suggested release tags

- `splitwise`
- `python`
- `cli`
- `oauth2`
- `codex`
- `claude-code`
- `personal-finance`
