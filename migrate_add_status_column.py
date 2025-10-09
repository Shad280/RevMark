"""
One-off migration: add `status` column to `request` table if it doesn't exist.
Run in production as a one-off command (example: via Railway run or `python migrate_add_status_column.py` with DATABASE_URL set).
"""
import os
import sys
from sqlalchemy import text

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from revmark import create_app, db
from sqlalchemy import inspect


def add_status_column():
    app = create_app()
    with app.app_context():
        engine = db.get_engine(app)
        inspector = inspect(engine)

        if 'request' not in inspector.get_table_names():
            print("Table 'request' does not exist. Nothing to do.")
            return True

        columns = [c['name'] for c in inspector.get_columns('request')]
        if 'status' in columns:
            print("Column 'status' already exists on 'request' table. Nothing to do.")
            return True

        try:
            print("Adding column 'status' to table 'request'...")
            # Add column with default 'open'
            db.session.execute(text("ALTER TABLE request ADD COLUMN status VARCHAR(20) DEFAULT 'open'"))
            # Create index if it doesn't exist (Postgres supports IF NOT EXISTS)
            try:
                db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_request_status ON request (status)"))
            except Exception:
                # Older PG versions: fallback to trying without IF NOT EXISTS
                try:
                    db.session.execute(text("CREATE INDEX ix_request_status ON request (status)"))
                except Exception:
                    print("Could not create index ix_request_status, continuing...")

            db.session.commit()
            print("✅ Column 'status' added and index created (if possible).")
            return True
        except Exception as e:
            print("❌ Failed to add column 'status':", str(e))
            db.session.rollback()
            return False


if __name__ == '__main__':
    ok = add_status_column()
    if not ok:
        sys.exit(1)

