# Commands

## Global flags

- `--api-key`
- `--client-id`
- `--client-secret`
- `--token-file`
- `--auth-file`
- `--json`

## Auth

- `auth-url`
- `exchange-code`
- `exchange-callback`
- `refresh`
- `check-auth`

## Users

- `get-current-user`
- `get-user --id <user_id>`
- `update-user --id <user_id> [fields...]`

Example:

```bash
python3 scripts/splitwise_connect.py update-user \
  --id 12345 \
  --default-currency EUR \
  --locale en
```

## Groups

- `list-groups`
- `get-group --id <group_id>`
- `create-group`
- `delete-group --id <group_id>`
- `undelete-group --id <group_id>`
- `add-user-to-group`
- `remove-user-from-group`

Create group examples:

```bash
python3 scripts/splitwise_connect.py create-group \
  --name "Trip Fund" \
  --group-type trip \
  --member "email=person@example.com,first_name=First,last_name=Last"
```

```bash
python3 scripts/splitwise_connect.py create-group \
  --body-file examples/create-group.json
```

## Friends

- `list-friends`
- `get-friend --id <friend_id>`
- `create-friend`
- `create-friends`
- `delete-friend --id <friend_id>`

## Expenses

- `list-expenses`
- `get-expense --id <expense_id>`
- `create-expense`
- `update-expense --id <expense_id>`
- `delete-expense --id <expense_id>`
- `undelete-expense --id <expense_id>`

Common expense fields:

- `--cost`
- `--description`
- `--details`
- `--date`
- `--repeat-interval`
- `--currency-code`
- `--category-id`
- `--group-id`
- `--split-equally`
- `--share`

Share format:

```text
user_id=123,paid_share=25,owed_share=0
```

Two-person outside-group example:

```bash
python3 scripts/splitwise_connect.py create-expense \
  --cost 500 \
  --description "Dinner" \
  --currency-code PKR \
  --share "user_id=111,paid_share=500,owed_share=250" \
  --share "user_id=222,paid_share=0,owed_share=250"
```

## Comments

- `get-comments --expense-id <expense_id>`
- `create-comment`
- `delete-comment --id <comment_id>`

## Notifications

- `get-notifications`

## Reference data

- `list-currencies`
- `list-categories`

## Raw helpers

- `api-get --path /endpoint`
- `api-post --path /endpoint`

Example:

```bash
python3 scripts/splitwise_connect.py api-get \
  --path /get_expenses \
  --body-json '{"limit": 5}'
```

```bash
python3 scripts/splitwise_connect.py api-post \
  --path /create_comment \
  --body-file examples/create-comment.json
```

## JSON input helpers

Some commands accept:

- `--body-json '{"key":"value"}'`
- `--body-file path/to/file.json`

This makes it easier to use advanced or less common payload fields without changing the CLI itself.
