from revmark import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    res = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='request' ORDER BY ordinal_position"))
    cols = [r[0] for r in res]
    print(cols)
