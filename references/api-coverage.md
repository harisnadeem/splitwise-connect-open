# Splitwise API Coverage

This skill covers the documented Splitwise API v3.0 areas:

- Users
  - `GET /get_current_user`
  - `GET /get_user/{id}`
  - `POST /update_user/{id}`
- Groups
  - `GET /get_groups`
  - `GET /get_group/{id}`
  - `POST /create_group`
  - `POST /delete_group/{id}`
  - `POST /undelete_group/{id}`
  - `POST /add_user_to_group`
  - `POST /remove_user_from_group`
- Friends
  - `GET /get_friends`
  - `GET /get_friend/{id}`
  - `POST /create_friend`
  - `POST /create_friends`
  - `POST /delete_friend/{id}`
- Expenses
  - `GET /get_expenses`
  - `GET /get_expense/{id}`
  - `POST /create_expense`
  - `POST /update_expense/{id}`
  - `POST /delete_expense/{id}`
  - `POST /undelete_expense/{id}`
- Comments
  - `GET /get_comments`
  - `POST /create_comment`
  - `POST /delete_comment/{id}`
- Notifications
  - `GET /get_notifications`
- Other
  - `GET /get_currencies`
  - `GET /get_categories`

The CLI also includes:

- OAuth2 helpers
- Raw `api-get`
- Raw `api-post`
