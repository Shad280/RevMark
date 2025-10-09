"""
One-off migration: add Stripe-related columns to `user` table if missing.
Run in production as a one-off command (example: via Railway run or `python migrate_add_user_stripe_columns.py` with DATABASE_URL set).
"""
import os
import sys
from sqlalchemy import text

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from revmark import create_app, db
from sqlalchemy import inspect


def add_user_stripe_columns():
    app = create_app()
    with app.app_context():
        engine = db.get_engine(app)
        inspector = inspect(engine)

        if 'user' not in inspector.get_table_names():
            # Table might be named "user" or user depending on DB; check both
            print("Table 'user' does not exist. Nothing to do.")
            return True

        columns = [c['name'] for c in inspector.get_columns('user')]

        actions = [
            ("stripe_account_id", "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS stripe_account_id VARCHAR(100)", "CREATE INDEX IF NOT EXISTS ix_user_stripe_account_id ON \"user\" (stripe_account_id)"),
            ("stripe_onboarding_complete", "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS stripe_onboarding_complete BOOLEAN DEFAULT FALSE", ""),
        ]

        any_changed = False

        for col_name, add_sql, index_sql in actions:
            if col_name in columns:
                print(f"Column '{col_name}' already exists. Skipping.")
                continue

            try:
                print(f"Adding column '{col_name}'...")
                db.session.execute(text(add_sql))
                if index_sql:
                    try:
                        db.session.execute(text(index_sql))
                    except Exception:
                        try:
                            db.session.execute(text(index_sql.replace(' IF NOT EXISTS', '')))
                        except Exception:
                            print(f"Could not create index for '{col_name}', continuing...")

                db.session.commit()
                print(f"✅ Column '{col_name}' added (and index attempted if provided).")
                any_changed = True
            except Exception as e:
                print(f"❌ Failed to add column '{col_name}':", str(e))
                db.session.rollback()
                return False

        if not any_changed:
            print("No columns needed to be added. Nothing to do.")

        return True


if __name__ == '__main__':
    ok = add_user_stripe_columns()
    if not ok:
        sys.exit(1)
