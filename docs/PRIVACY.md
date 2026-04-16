# Privacy Notes

This document covers privacy-sensitive data handling for contributors and maintainers.

## What should never be committed

- API keys
- OAuth client secrets
- access tokens
- refresh tokens
- callback URLs containing codes
- exported account responses with real names, emails, balances, comments, or IDs
- screenshots of private account data

## Current protections

- token files are gitignored
- auth-session files are gitignored
- examples use placeholders only
- docs avoid real account data

## Pre-release scrub checklist

1. Search for your real name, email addresses, friend names, and common account IDs.
2. Search for `access_token`, `refresh_token`, `client_secret`, and `api_key`.
3. Review example payloads for accidental live IDs.
4. Review shell history snippets before copying them into docs.
5. Inspect `git diff` before publishing.

## Safe placeholders

Use:

- `person@example.com`
- `12345`
- `Trip Fund`
- `Dinner`

Do not use real friend names or live Splitwise resource IDs in public docs.
