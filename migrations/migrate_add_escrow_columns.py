"""
One-off migration: add escrow/payment related columns to `request` table if missing.
"""
import os
import sys
from sqlalchemy import text

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from revmark import create_app, db
from sqlalchemy import inspect


def add_escrow_columns():
    app = create_app()
    with app.app_context():
        engine = db.get_engine(app)
        inspector = inspect(engine)

        if 'request' not in inspector.get_table_names():
            print("Table 'request' does not exist. Nothing to do.")
            return True

        columns = [c['name'] for c in inspector.get_columns('request')]

        actions = [
            ("seller_id", "ALTER TABLE request ADD COLUMN IF NOT EXISTS seller_id INTEGER" , "CREATE INDEX IF NOT EXISTS ix_request_seller_id ON request (seller_id)"),
            ("stripe_payment_intent_id", "ALTER TABLE request ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR(100)", "CREATE INDEX IF NOT EXISTS ix_request_stripe_payment_intent_id ON request (stripe_payment_intent_id)"),
            ("stripe_transfer_id", "ALTER TABLE request ADD COLUMN IF NOT EXISTS stripe_transfer_id VARCHAR(100)", "CREATE INDEX IF NOT EXISTS ix_request_stripe_transfer_id ON request (stripe_transfer_id)"),
            ("escrow_amount", "ALTER TABLE request ADD COLUMN IF NOT EXISTS escrow_amount DOUBLE PRECISION", "CREATE INDEX IF NOT EXISTS ix_request_escrow_amount ON request (escrow_amount)"),
            ("platform_fee", "ALTER TABLE request ADD COLUMN IF NOT EXISTS platform_fee DOUBLE PRECISION", "CREATE INDEX IF NOT EXISTS ix_request_platform_fee ON request (platform_fee)"),
        ]

        any_changed = False

        for col_name, add_sql, index_sql in actions:
            if col_name in columns:
                print(f"Column '{col_name}' already exists. Skipping.")
                continue

            try:
                print(f"Adding column '{col_name}'...")
                db.session.execute(text(add_sql))
                try:
                    db.session.execute(text(index_sql))
                except Exception:
                    try:
                        idx_sql = index_sql.replace(' IF NOT EXISTS', '')
                        db.session.execute(text(idx_sql))
                    except Exception:
                        print(f"Could not create index for '{col_name}', continuing...")

                db.session.commit()
                print(f"✅ Column '{col_name}' added (and index attempted).")
                any_changed = True
            except Exception as e:
                print(f"❌ Failed to add column '{col_name}':", str(e))
                db.session.rollback()
                return False

        if not any_changed:
            print("No columns needed to be added. Nothing to do.")

        return True


if __name__ == '__main__':
    ok = add_escrow_columns()
    if not ok:
        sys.exit(1)
