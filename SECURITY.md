# Security

## Reporting a problem

If you discover a security issue in this repository, avoid posting secrets, tokens, or exploitable details publicly in an issue. Share a minimal reproduction and rotate any exposed credentials immediately.

## Secrets handling

- Keep `SPLITWISE_API_KEY`, `SPLITWISE_OAUTH_CLIENT_ID`, and `SPLITWISE_OAUTH_CLIENT_SECRET` out of the repo.
- Token files and OAuth auth-session files are intentionally gitignored.
- Do not commit shell history snippets containing real credentials.

## Sensitive data

Splitwise data can include names, emails, balances, comments, and group membership. Treat real API responses as private unless they have been explicitly scrubbed.
