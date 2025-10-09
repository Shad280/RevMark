import traceback

try:
    from revmark import create_app
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        resp = c.get('/')
        print('STATUS:', resp.status_code)
        try:
            print(resp.get_data(as_text=True))
        except Exception:
            pass
except Exception:
    print('EXCEPTION WHEN CALLING /:')
    traceback.print_exc()
    raise
