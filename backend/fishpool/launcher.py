"""Windows launcher that migrates Fishpool data and opens the local web app."""

import os
import socket
import threading
import time
import traceback
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


HOST = '127.0.0.1'
PORT_RANGE = range(8765, 8786)


def _is_fishpool_running(port):
    """检查指定端口是否已经运行本应用。"""
    try:
        with urlopen(f'http://{HOST}:{port}/health/', timeout=0.5) as response:
            return response.read() == b'ok'
    except (URLError, OSError):
        return False


def _can_bind(port):
    """判断端口是否可供本次启动使用。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((HOST, port))
            return True
        except OSError:
            return False


def _find_server_port():
    """返回已有 Fishpool 服务或首个可用本机端口。"""
    for port in PORT_RANGE:
        if _is_fishpool_running(port):
            return port, True
        if _can_bind(port):
            return port, False
    raise RuntimeError('Fishpool 无法找到可用的本机服务端口。')


def _open_browser_when_ready(port):
    """等待 Waitress 就绪后在默认浏览器中打开 Fishpool。"""
    url = f'http://{HOST}:{port}/'
    for _ in range(100):
        if _is_fishpool_running(port):
            webbrowser.open(url)
            return
        time.sleep(0.1)


def main():
    """初始化用户数据库，启动本机服务并自动打开浏览器。"""
    os.environ['FISHPOOL_PACKAGED'] = '1'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fishpool.settings')

    from fishpool.runtime import get_data_directory

    data_directory = get_data_directory()
    data_directory.mkdir(parents=True, exist_ok=True)
    log_path = data_directory / 'launcher.log'

    try:
        import django
        from django.core.management import call_command
        from waitress import serve

        django.setup()
        call_command('migrate', interactive=False, verbosity=0)
        port, already_running = _find_server_port()
        if already_running:
            webbrowser.open(f'http://{HOST}:{port}/')
            return

        from fishpool.wsgi import application

        threading.Thread(target=_open_browser_when_ready, args=(port,), daemon=True).start()
        serve(application, host=HOST, port=port, threads=4)
    except Exception:
        log_path.write_text(traceback.format_exc(), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
