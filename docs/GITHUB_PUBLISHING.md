# GitHub Publishing

## Suggested repository name

`splitwise-connect-open`

## Suggested short description

Comprehensive Splitwise CLI and Zo skill with API key and OAuth2 auth, full endpoint coverage, and Cloudflare-friendly requests.

## Suggested topics

- `splitwise`
- `python`
- `cli`
- `oauth2`
- `api-client`
- `cloudscraper`
- `zo-computer`
- `personal-finance`

## Suggested About section

Public, sanitized Splitwise integration for Zo Computer and terminal workflows. Supports API key auth, OAuth2, full documented endpoint coverage, and raw helpers for advanced payloads.

## Suggested initial release

### Tag

`v0.1.0`

### Title

`splitwise-connect-open v0.1.0`

### Release notes

```markdown
## Highlights

- Added a public, sanitized Splitwise skill and CLI for Zo Computer
- Supports both personal API key auth and OAuth2
- Covers users, groups, friends, expenses, comments, notifications, currencies, and categories
- Includes raw `api-get` and `api-post` helpers for future-proofing
- Uses `cloudscraper` to handle Cloudflare-protected Splitwise requests more reliably

## Included documentation

- Quick-start README
- Authentication guide
- Detailed command reference
- Privacy and sanitization notes
- Release checklist
- Example JSON payloads

## Notes

- No personal account data, tokens, or private examples are included
- Token and auth-session files are gitignored by default
```

## Suggested first push flow

```bash
cd /home/workspace/Skills/splitwise-connect-open
git remote add origin <your-github-repo-url>
git push -u origin main
git tag v0.1.0
git push origin v0.1.0
```
