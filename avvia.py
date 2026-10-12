import os
import sys
import threading
import webbrowser


def main():
    if sys.platform == 'win32':
        # Necessario per subprocess asincroni Docker su Windows.
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    from app.config import load_settings
    from app.main import create_app
    import uvicorn
    settings = load_settings()
    url = f'http://127.0.0.1:{settings.port}'
    print('Officina — assistente personale')
    print('Apri nel browser:', url)
    print('Per chiudere: Ctrl+C. Memoria e progetti restano sul disco.')
    if '--no-browser' not in sys.argv:
        timer = threading.Timer(1.5, lambda: webbrowser.open(url))
        timer.daemon = True
        timer.start()
    uvicorn.run(create_app(settings), host='127.0.0.1', port=settings.port, access_log=False)


if __name__ == '__main__':
    main()
