#!/usr/bin/env python3
import argparse
import json
import os
import secrets
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import cloudscraper
except ImportError as exc:
    cloudscraper = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

API_BASE = "https://secure.splitwise.com/api/v3.0"
AUTH_URL = "https://secure.splitwise.com/oauth/authorize"
TOKEN_URL = "https://secure.splitwise.com/oauth/token"

SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE = Path(__file__).resolve().with_name("requirements.txt")
DEFAULT_TOKEN_FILE = SKILL_ROOT / "splitwise_token.json"
DEFAULT_AUTH_FILE = SKILL_ROOT / "splitwise_auth_session.json"


class SplitwiseError(Exception):
    pass


def _require_cloudscraper() -> None:
    if cloudscraper is None:
        raise SplitwiseError(
            "cloudscraper is required. Install it with: pip install -r "
            f"{REQUIREMENTS_FILE}"
        ) from _IMPORT_ERROR


def _scraper():
    _require_cloudscraper()
    return cloudscraper.create_scraper()


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    os.chmod(path, 0o600)


def _load_json(path: Path, missing_message: str) -> Dict[str, Any]:
    if not path.exists():
        raise SplitwiseError(missing_message)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SplitwiseError(f"Invalid JSON in {path}: {exc}") from exc


def _client_id(args: argparse.Namespace) -> str:
    value = args.client_id or os.getenv("SPLITWISE_OAUTH_CLIENT_ID")
    if not value:
        raise SplitwiseError(
            "Missing client ID. Pass --client-id or set SPLITWISE_OAUTH_CLIENT_ID."
        )
    return value.strip()


def _client_secret(args: argparse.Namespace) -> str:
    value = args.client_secret or os.getenv("SPLITWISE_OAUTH_CLIENT_SECRET")
    if not value:
        raise SplitwiseError(
            "Missing client secret. Pass --client-secret or set SPLITWISE_OAUTH_CLIENT_SECRET."
        )
    return value.strip()


def _api_key(args: argparse.Namespace) -> Optional[str]:
    value = args.api_key or os.getenv("SPLITWISE_API_KEY")
    return value.strip() if value else None


def _parse_callback_url(callback_url: str) -> Tuple[str, Optional[str], str]:
    parsed = urllib.parse.urlparse(callback_url)
    query = urllib.parse.parse_qs(parsed.query)
    code = query.get("code", [None])[0]
    state = query.get("state", [None])[0]
    error = query.get("error", [None])[0]
    if error:
        description = query.get("error_description", ["Authorization failed"])[0]
        raise SplitwiseError(f"{error}: {description}")
    if not code:
        raise SplitwiseError("Callback URL does not contain a `code` parameter.")
    redirect_uri = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return code, state, redirect_uri


def _token_expired(token: Dict[str, Any], skew_seconds: int = 60) -> bool:
    obtained_at = int(token.get("obtained_at", 0))
    expires_in = int(token.get("expires_in", 0))
    if not obtained_at or not expires_in:
        return True
    return int(time.time()) + skew_seconds >= obtained_at + expires_in


def _save_token(path: Path, token: Dict[str, Any]) -> None:
    token["obtained_at"] = int(time.time())
    _atomic_write_json(path, token)


def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    form: Optional[Dict[str, Any]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    request_headers = dict(headers or {})
    scraper = _scraper()
    response = scraper.request(
        method=method,
        url=url,
        headers=request_headers,
        params={k: v for k, v in (params or {}).items() if v is not None},
        data={k: v for k, v in (form or {}).items() if v is not None} if form is not None else None,
        json=json_payload,
        timeout=45,
    )
    if response.status_code >= 400:
        raise SplitwiseError(f"HTTP {response.status_code} from {url}: {response.text}")
    if not response.text.strip():
        return {}
    try:
        return response.json()
    except ValueError as exc:
        raise SplitwiseError(f"Non-JSON response from {url}: {response.text}") from exc


def _refresh_oauth_token(args: argparse.Namespace, token: Dict[str, Any]) -> Dict[str, Any]:
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise SplitwiseError("No refresh token found. Re-authorize first.")
    refreshed = _http_json(
        TOKEN_URL,
        method="POST",
        form={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": _client_id(args),
            "client_secret": _client_secret(args),
        },
    )
    if "access_token" not in refreshed:
        raise SplitwiseError(f"Refresh failed: {json.dumps(refreshed)}")
    if "refresh_token" not in refreshed:
        refreshed["refresh_token"] = refresh_token
    return refreshed


def _oauth_access_token(args: argparse.Namespace) -> str:
    token_path = Path(args.token_file)
    token = _load_json(token_path, f"Token file not found: {token_path}")
    if _token_expired(token):
        token = _refresh_oauth_token(args, token)
        _save_token(token_path, token)
    access = token.get("access_token")
    if not access:
        raise SplitwiseError("Stored OAuth token has no access_token.")
    return access


def _bearer_token(args: argparse.Namespace) -> str:
    key = _api_key(args)
    if key:
        return key
    return _oauth_access_token(args)


def _api_get(
    args: argparse.Namespace,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    requires_auth: bool = True,
) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {_bearer_token(args)}"} if requires_auth else {}
    return _http_json(API_BASE + path, headers=headers, params=params)


def _api_post(
    args: argparse.Namespace,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
    *,
    requires_auth: bool = True,
    content_type: str = "form",
) -> Dict[str, Any]:
    headers: Dict[str, str] = {}
    if requires_auth:
        headers["Authorization"] = f"Bearer {_bearer_token(args)}"
    payload = payload or {}
    if content_type == "json":
        return _http_json(API_BASE + path, method="POST", headers=headers, json_payload=payload)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    return _http_json(API_BASE + path, method="POST", headers=headers, form=payload)


def _print(args: argparse.Namespace, payload: Any) -> None:
    if args.json or not isinstance(payload, str):
        print(json.dumps(payload, indent=2))
    else:
        print(payload)


def _ensure_success(result: Dict[str, Any]) -> Dict[str, Any]:
    errors = result.get("errors")
    if isinstance(errors, dict) and errors:
        raise SplitwiseError(f"Splitwise returned errors: {json.dumps(errors)}")
    if result.get("success") is False:
        raise SplitwiseError(f"Splitwise returned success=false: {json.dumps(result)}")
    return result


def _parse_kv_items(raw: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for part in raw.split(","):
        item = part.strip()
        if not item:
            continue
        if "=" not in item:
            raise SplitwiseError(f"Invalid item `{item}`. Expected key=value format.")
        key, value = item.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def _flatten_records(records: Iterable[str], *, prefix: str = "users") -> Dict[str, str]:
    flattened: Dict[str, str] = {}
    for index, raw in enumerate(records):
        record = _parse_kv_items(raw)
        for key, value in record.items():
            flattened[f"{prefix}__{index}__{key}"] = value
    return flattened


def _load_payload(args: argparse.Namespace) -> Dict[str, Any]:
    if getattr(args, "body_json", None):
        try:
            payload = json.loads(args.body_json)
        except json.JSONDecodeError as exc:
            raise SplitwiseError(f"Invalid JSON passed to --body-json: {exc}") from exc
        if not isinstance(payload, dict):
            raise SplitwiseError("--body-json must decode to an object.")
        return payload
    if getattr(args, "body_file", None):
        body_path = Path(args.body_file)
        return _load_json(body_path, f"JSON body file not found: {body_path}")
    return {}


def _merge_payload(*parts: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for part in parts:
        for key, value in part.items():
            if value is not None:
                merged[key] = value
    return merged


def _common_expense_fields(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "cost": str(args.cost) if args.cost is not None else None,
        "description": args.description,
        "details": args.details,
        "date": args.date,
        "repeat_interval": args.repeat_interval,
        "currency_code": args.currency_code,
        "category_id": args.category_id,
        "group_id": args.group_id,
        "split_equally": "true" if getattr(args, "split_equally", False) else None,
    }


def _format_user_name(user: Dict[str, Any]) -> str:
    return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Unknown"


def cmd_auth_url(args: argparse.Namespace) -> int:
    state = args.state or secrets.token_urlsafe(32)
    auth_session = {
        "state": state,
        "redirect_uri": args.redirect_uri,
        "scope": args.scope,
        "created_at": int(time.time()),
        "client_id": _client_id(args),
    }
    _atomic_write_json(Path(args.auth_file), auth_session)
    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": _client_id(args),
            "redirect_uri": args.redirect_uri,
            "state": state,
            "scope": args.scope,
        }
    )
    print(AUTH_URL + "?" + query)
    print(f"Saved auth session to: {args.auth_file}")
    return 0


def cmd_exchange_code(args: argparse.Namespace) -> int:
    token = _http_json(
        TOKEN_URL,
        method="POST",
        form={
            "grant_type": "authorization_code",
            "code": args.code,
            "redirect_uri": args.redirect_uri,
            "client_id": _client_id(args),
            "client_secret": _client_secret(args),
        },
    )
    if "access_token" not in token:
        raise SplitwiseError(f"Token exchange failed: {json.dumps(token)}")
    _save_token(Path(args.token_file), token)
    print(f"OAuth token saved to: {args.token_file}")
    return 0


def cmd_exchange_callback(args: argparse.Namespace) -> int:
    code, state, callback_redirect_uri = _parse_callback_url(args.callback_url)
    auth = _load_json(
        Path(args.auth_file),
        f"Auth session file not found: {args.auth_file}. Run auth-url first.",
    )
    if auth.get("state") and state != auth.get("state"):
        raise SplitwiseError("State mismatch in callback URL.")
    if auth.get("redirect_uri") and callback_redirect_uri != auth.get("redirect_uri"):
        raise SplitwiseError(
            f"Redirect URI mismatch. Expected `{auth.get('redirect_uri')}` but got `{callback_redirect_uri}`."
        )
    forwarded = argparse.Namespace(**vars(args))
    forwarded.code = code
    forwarded.redirect_uri = auth.get("redirect_uri")
    return cmd_exchange_code(forwarded)


def cmd_refresh(args: argparse.Namespace) -> int:
    token_path = Path(args.token_file)
    token = _load_json(token_path, f"Token file not found: {token_path}")
    new_token = _refresh_oauth_token(args, token)
    _save_token(token_path, new_token)
    print(f"Token refreshed and saved to: {args.token_file}")
    return 0


def cmd_check_auth(args: argparse.Namespace) -> int:
    data = _api_get(args, "/get_current_user")
    user = data.get("user", {})
    print(f"Connected as: {_format_user_name(user)} (id={user.get('id')})")
    print(f"Email: {user.get('email', 'unknown')}")
    print(f"Default currency: {user.get('default_currency', 'unknown')}")
    return 0


def cmd_get_current_user(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, "/get_current_user"))
    return 0


def cmd_get_user(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, f"/get_user/{args.id}"))
    return 0


def cmd_update_user(args: argparse.Namespace) -> int:
    payload = _merge_payload(
        _load_payload(args),
        {
            "first_name": args.first_name,
            "last_name": args.last_name,
            "email": args.email,
            "password": args.password,
            "locale": args.locale,
            "default_currency": args.default_currency,
        },
    )
    _print(args, _api_post(args, f"/update_user/{args.id}", payload))
    return 0


def cmd_list_groups(args: argparse.Namespace) -> int:
    data = _api_get(args, "/get_groups")
    groups = data.get("groups", [])
    if args.json:
        _print(args, data)
        return 0
    print(f"Total groups: {len(groups)}")
    for group in groups:
        print(
            f"[{group.get('id')}] {group.get('name')} | type={group.get('group_type')} | "
            f"members={len(group.get('members', []))} | simplify={group.get('simplify_by_default')}"
        )
    return 0


def cmd_get_group(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, f"/get_group/{args.id}"))
    return 0


def cmd_create_group(args: argparse.Namespace) -> int:
    payload = _merge_payload(
        _load_payload(args),
        {
            "name": args.name,
            "group_type": args.group_type,
            "simplify_by_default": "true" if args.simplify_by_default else None,
        },
        _flatten_records(args.member),
    )
    _print(args, _api_post(args, "/create_group", payload))
    return 0


def cmd_delete_group(args: argparse.Namespace) -> int:
    _print(args, _ensure_success(_api_post(args, f"/delete_group/{args.id}", {})))
    return 0


def cmd_undelete_group(args: argparse.Namespace) -> int:
    _print(args, _ensure_success(_api_post(args, f"/undelete_group/{args.id}", {})))
    return 0


def cmd_add_user_to_group(args: argparse.Namespace) -> int:
    payload = _merge_payload(
        _load_payload(args),
        {
            "group_id": args.group_id,
            "user_id": args.user_id,
            "first_name": args.first_name,
            "last_name": args.last_name,
            "email": args.email,
        },
    )
    _print(args, _ensure_success(_api_post(args, "/add_user_to_group", payload)))
    return 0


def cmd_remove_user_from_group(args: argparse.Namespace) -> int:
    payload = _merge_payload(_load_payload(args), {"group_id": args.group_id, "user_id": args.user_id})
    _print(args, _ensure_success(_api_post(args, "/remove_user_from_group", payload)))
    return 0


def cmd_list_friends(args: argparse.Namespace) -> int:
    data = _api_get(args, "/get_friends")
    friends = data.get("friends", [])
    if args.json:
        _print(args, data)
        return 0
    print(f"Total friends: {len(friends)}")
    print(f"{'ID':<12} {'Name':<28} {'Email':<40} Balance")
    print("-" * 100)
    for friend in friends:
        balance = ", ".join(
            f"{item.get('amount')} {item.get('currency_code')}" for item in friend.get("balance", [])
        ) or "0"
        print(
            f"{friend.get('id', ''):<12} {_format_user_name(friend):<28} "
            f"{friend.get('email', ''):<40} {balance}"
        )
    return 0


def cmd_get_friend(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, f"/get_friend/{args.id}"))
    return 0


def cmd_create_friend(args: argparse.Namespace) -> int:
    payload = _merge_payload(
        _load_payload(args),
        {
            "user_email": args.user_email,
            "user_first_name": args.user_first_name,
            "user_last_name": args.user_last_name,
        },
    )
    _print(args, _api_post(args, "/create_friend", payload))
    return 0


def cmd_create_friends(args: argparse.Namespace) -> int:
    payload = _merge_payload(_load_payload(args), _flatten_records(args.friend))
    _print(args, _api_post(args, "/create_friends", payload))
    return 0


def cmd_delete_friend(args: argparse.Namespace) -> int:
    _print(args, _ensure_success(_api_post(args, f"/delete_friend/{args.id}", {})))
    return 0


def cmd_list_expenses(args: argparse.Namespace) -> int:
    data = _api_get(
        args,
        "/get_expenses",
        {
            "group_id": args.group_id,
            "friend_id": args.friend_id,
            "dated_after": args.dated_after,
            "dated_before": args.dated_before,
            "updated_after": args.updated_after,
            "updated_before": args.updated_before,
            "limit": args.limit,
            "offset": args.offset,
        },
    )
    expenses = data.get("expenses", [])
    if args.json:
        _print(args, data)
        return 0
    print(f"Showing {len(expenses)} expense(s)")
    print(f"{'ID':<14} {'Description':<36} {'Amount':<16} {'Date':<12}")
    print("-" * 84)
    for expense in expenses:
        amount = f"{expense.get('cost')} {expense.get('currency_code')}"
        print(
            f"{expense.get('id', ''):<14} {expense.get('description', '')[:36]:<36} "
            f"{amount:<16} {str(expense.get('date', ''))[:10]:<12}"
        )
    return 0


def cmd_get_expense(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, f"/get_expense/{args.id}"))
    return 0


def cmd_create_expense(args: argparse.Namespace) -> int:
    payload = _merge_payload(_load_payload(args), _common_expense_fields(args), _flatten_records(args.share))
    _print(args, _ensure_success(_api_post(args, "/create_expense", payload)))
    return 0


def cmd_update_expense(args: argparse.Namespace) -> int:
    payload = _merge_payload(_load_payload(args), _common_expense_fields(args), _flatten_records(args.share))
    _print(args, _ensure_success(_api_post(args, f"/update_expense/{args.id}", payload)))
    return 0


def cmd_delete_expense(args: argparse.Namespace) -> int:
    _print(args, _ensure_success(_api_post(args, f"/delete_expense/{args.id}", {})))
    return 0


def cmd_undelete_expense(args: argparse.Namespace) -> int:
    _print(args, _ensure_success(_api_post(args, f"/undelete_expense/{args.id}", {})))
    return 0


def cmd_get_comments(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, "/get_comments", {"expense_id": args.expense_id}))
    return 0


def cmd_create_comment(args: argparse.Namespace) -> int:
    payload = _merge_payload(_load_payload(args), {"expense_id": args.expense_id, "content": args.content})
    _print(args, _api_post(args, "/create_comment", payload))
    return 0


def cmd_delete_comment(args: argparse.Namespace) -> int:
    _print(args, _api_post(args, f"/delete_comment/{args.id}", {}))
    return 0


def cmd_get_notifications(args: argparse.Namespace) -> int:
    _print(
        args,
        _api_get(
            args,
            "/get_notifications",
            {"updated_after": args.updated_after, "limit": args.limit},
        ),
    )
    return 0


def cmd_list_currencies(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, "/get_currencies", requires_auth=False))
    return 0


def cmd_list_categories(args: argparse.Namespace) -> int:
    _print(args, _api_get(args, "/get_categories", requires_auth=False))
    return 0


def cmd_api_get(args: argparse.Namespace) -> int:
    params = _load_payload(args)
    _print(args, _api_get(args, args.path, params or None, requires_auth=not args.no_auth))
    return 0


def cmd_api_post(args: argparse.Namespace) -> int:
    payload = _load_payload(args)
    _print(
        args,
        _api_post(
            args,
            args.path,
            payload,
            requires_auth=not args.no_auth,
            content_type=args.content_type,
        ),
    )
    return 0


def _add_auth_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", help="Splitwise API key. Defaults to SPLITWISE_API_KEY.")
    parser.add_argument("--client-id", help="OAuth client ID. Defaults to SPLITWISE_OAUTH_CLIENT_ID.")
    parser.add_argument(
        "--client-secret",
        help="OAuth client secret. Defaults to SPLITWISE_OAUTH_CLIENT_SECRET.",
    )
    parser.add_argument("--token-file", default=str(DEFAULT_TOKEN_FILE), help="OAuth token JSON path.")
    parser.add_argument("--auth-file", default=str(DEFAULT_AUTH_FILE), help="OAuth auth-session JSON path.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Always print raw JSON instead of human-friendly summaries.",
    )


def _add_body_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--body-json", help="JSON object payload string.")
    parser.add_argument("--body-file", help="Path to a JSON object file.")


def _add_common_expense_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cost", help="Expense amount.")
    parser.add_argument("--description", help="Short expense description.")
    parser.add_argument("--details", help="Longer notes field.")
    parser.add_argument("--date", help="Expense date/time in ISO format.")
    parser.add_argument(
        "--repeat-interval",
        choices=["never", "weekly", "fortnightly", "monthly", "yearly"],
        help="Recurring expense cadence.",
    )
    parser.add_argument("--currency-code", help="Currency code such as USD, PKR, EUR.")
    parser.add_argument("--category-id", type=int, help="Splitwise subcategory ID.")
    parser.add_argument("--group-id", type=int, help="Group ID, or 0 for outside a group.")
    parser.add_argument(
        "--split-equally",
        action="store_true",
        help="Create an equal group split. Requires --group-id.",
    )
    parser.add_argument(
        "--share",
        action="append",
        default=[],
        help=(
            "Repeatable share entry in key=value form, comma-separated. "
            "Example: user_id=123,paid_share=25,owed_share=0"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Comprehensive Splitwise CLI for API key and OAuth2 workflows."
    )
    _add_auth_arguments(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("auth-url", help="Generate the OAuth2 authorization URL.")
    p.add_argument("--redirect-uri", required=True)
    p.add_argument("--state")
    p.add_argument("--scope", default="")
    p.set_defaults(func=cmd_auth_url)

    p = sub.add_parser("exchange-code", help="Exchange an OAuth code for a token.")
    p.add_argument("--code", required=True)
    p.add_argument("--redirect-uri", required=True)
    p.set_defaults(func=cmd_exchange_code)

    p = sub.add_parser("exchange-callback", help="Exchange a full OAuth callback URL for a token.")
    p.add_argument("--callback-url", required=True)
    p.set_defaults(func=cmd_exchange_callback)

    p = sub.add_parser("refresh", help="Refresh the stored OAuth token.")
    p.set_defaults(func=cmd_refresh)

    p = sub.add_parser("check-auth", help="Validate the current API key or OAuth token.")
    p.set_defaults(func=cmd_check_auth)

    p = sub.add_parser("get-current-user", help="Fetch the authenticated user profile.")
    p.set_defaults(func=cmd_get_current_user)

    p = sub.add_parser("get-user", help="Fetch another user by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_user)

    p = sub.add_parser("update-user", help="Update a user profile.")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--first-name")
    p.add_argument("--last-name")
    p.add_argument("--email")
    p.add_argument("--password")
    p.add_argument("--locale")
    p.add_argument("--default-currency")
    _add_body_arguments(p)
    p.set_defaults(func=cmd_update_user)

    p = sub.add_parser("list-groups", help="List groups visible to the current user.")
    p.set_defaults(func=cmd_list_groups)

    p = sub.add_parser("get-group", help="Fetch a group by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_group)

    p = sub.add_parser("create-group", help="Create a group.")
    p.add_argument("--name")
    p.add_argument(
        "--group-type",
        choices=["home", "trip", "couple", "other", "apartment", "house"],
    )
    p.add_argument("--simplify-by-default", action="store_true")
    p.add_argument(
        "--member",
        action="append",
        default=[],
        help="Repeatable member entry. Example: user_id=123 or email=user@example.com,first_name=A,last_name=B",
    )
    _add_body_arguments(p)
    p.set_defaults(func=cmd_create_group)

    p = sub.add_parser("delete-group", help="Delete a group by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_delete_group)

    p = sub.add_parser("undelete-group", help="Restore a deleted group by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_undelete_group)

    p = sub.add_parser("add-user-to-group", help="Add a user to a group.")
    p.add_argument("--group-id", type=int)
    p.add_argument("--user-id", type=int)
    p.add_argument("--first-name")
    p.add_argument("--last-name")
    p.add_argument("--email")
    _add_body_arguments(p)
    p.set_defaults(func=cmd_add_user_to_group)

    p = sub.add_parser("remove-user-from-group", help="Remove a user from a group.")
    p.add_argument("--group-id", type=int)
    p.add_argument("--user-id", type=int)
    _add_body_arguments(p)
    p.set_defaults(func=cmd_remove_user_from_group)

    p = sub.add_parser("list-friends", help="List friends and balances.")
    p.set_defaults(func=cmd_list_friends)

    p = sub.add_parser("get-friend", help="Fetch a friend by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_friend)

    p = sub.add_parser("create-friend", help="Create a friendship.")
    p.add_argument("--user-email")
    p.add_argument("--user-first-name")
    p.add_argument("--user-last-name")
    _add_body_arguments(p)
    p.set_defaults(func=cmd_create_friend)

    p = sub.add_parser("create-friends", help="Create multiple friends in one call.")
    p.add_argument(
        "--friend",
        action="append",
        default=[],
        help="Repeatable friend entry. Example: email=user@example.com,first_name=A,last_name=B",
    )
    _add_body_arguments(p)
    p.set_defaults(func=cmd_create_friends)

    p = sub.add_parser("delete-friend", help="Delete a friendship by friend ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_delete_friend)

    p = sub.add_parser("list-expenses", help="List expenses with optional filters.")
    p.add_argument("--group-id", type=int)
    p.add_argument("--friend-id", type=int)
    p.add_argument("--dated-after")
    p.add_argument("--dated-before")
    p.add_argument("--updated-after")
    p.add_argument("--updated-before")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--offset", type=int, default=0)
    p.set_defaults(func=cmd_list_expenses)

    p = sub.add_parser("get-expense", help="Fetch an expense by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_expense)

    p = sub.add_parser("create-expense", help="Create an expense.")
    _add_common_expense_args(p)
    _add_body_arguments(p)
    p.set_defaults(func=cmd_create_expense)

    p = sub.add_parser("update-expense", help="Update an expense.")
    p.add_argument("--id", type=int, required=True)
    _add_common_expense_args(p)
    _add_body_arguments(p)
    p.set_defaults(func=cmd_update_expense)

    p = sub.add_parser("delete-expense", help="Delete an expense by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_delete_expense)

    p = sub.add_parser("undelete-expense", help="Restore a deleted expense by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_undelete_expense)

    p = sub.add_parser("get-comments", help="List comments for an expense.")
    p.add_argument("--expense-id", type=int, required=True)
    p.set_defaults(func=cmd_get_comments)

    p = sub.add_parser("create-comment", help="Create a comment on an expense.")
    p.add_argument("--expense-id", type=int)
    p.add_argument("--content")
    _add_body_arguments(p)
    p.set_defaults(func=cmd_create_comment)

    p = sub.add_parser("delete-comment", help="Delete a comment by ID.")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_delete_comment)

    p = sub.add_parser("get-notifications", help="Fetch notifications.")
    p.add_argument("--updated-after")
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(func=cmd_get_notifications)

    p = sub.add_parser("list-currencies", help="List supported currency codes.")
    p.set_defaults(func=cmd_list_currencies)

    p = sub.add_parser("list-categories", help="List supported expense categories.")
    p.set_defaults(func=cmd_list_categories)

    p = sub.add_parser("api-get", help="Raw GET helper for current or future endpoints.")
    p.add_argument("--path", required=True, help="API path such as /get_expenses")
    p.add_argument("--no-auth", action="store_true", help="Skip the Authorization header.")
    _add_body_arguments(p)
    p.set_defaults(func=cmd_api_get)

    p = sub.add_parser("api-post", help="Raw POST helper for current or future endpoints.")
    p.add_argument("--path", required=True, help="API path such as /create_expense")
    p.add_argument("--no-auth", action="store_true", help="Skip the Authorization header.")
    p.add_argument("--content-type", choices=["form", "json"], default="form")
    _add_body_arguments(p)
    p.set_defaults(func=cmd_api_post)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except SplitwiseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
