# GitHub Publishing

## Suggested repository name

`splitwise-connect-open`

## Suggested short description

Comprehensive Splitwise CLI and agent-friendly skill wrapper with API key and OAuth2 auth, full endpoint coverage, and Cloudflare-friendly requests.

## Suggested topics

- `splitwise`
- `python`
- `cli`
- `oauth2`
- `api-client`
- `cloudscraper`
- `codex`
- `claude-code`
- `personal-finance`

## Suggested About section

Splitwise integration for Codex, Claude Code, other terminal agents, and plain shell workflows. Supports API key auth, OAuth2, full documented endpoint coverage, and raw helpers for advanced payloads.

## Suggested initial release

### Tag

`v0.1.0`

### Title

`splitwise-connect-open v0.1.0`

### Release notes

```markdown
## Highlights

- Added a Splitwise CLI and skill wrapper for Codex, Claude Code, and terminal workflows
- Supports both personal API key auth and OAuth2
- Covers users, groups, friends, expenses, comments, notifications, currencies, and categories
- Includes raw `api-get` and `api-post` helpers for future-proofing
- Uses `cloudscraper` to handle Cloudflare-protected Splitwise requests more reliably

## Included documentation

- Quick-start README
- Authentication guide
- Detailed command reference
- Privacy notes
- Release checklist
- Example JSON payloads
```

## Suggested first push flow

```bash
cd splitwise-connect-open
git remote add origin <your-github-repo-url>
git push -u origin main
git tag v0.1.0
git push origin v0.1.0
```
