This folder contains one-off, idempotent migration scripts that were run directly in production to bring the database schema in line with the application models.

Files:
- `migrate_add_status_column.py` — added the `status` column to `request`.
- `migrate_add_escrow_columns.py` — added `seller_id`, `stripe_*`, `escrow_amount`, and `platform_fee` to `request`.
- `migrate_add_user_stripe_columns.py` — added `stripe_account_id` and `stripe_onboarding_complete` to `user`.
- `list_request_columns.py` (helper) — utility used to inspect the `request` table.

Notes:
- These scripts are retained for audit and reproducibility. Apply caution before re-running; they are idempotent but intended for one-off use.
