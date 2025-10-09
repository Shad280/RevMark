from revmark import create_app

try:
    app = create_app()
    print('LOCAL IMPORT: create_app() OK')
except Exception as e:
    print('LOCAL IMPORT: create_app() FAILED')
    import traceback
    traceback.print_exc()
    raise
