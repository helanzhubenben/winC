"""Fishpool packaged-runtime paths for user data and bundled resources."""

import os
import sys
from pathlib import Path


REGISTRY_PATH = r'Software\Fishpool'
REGISTRY_VALUE = 'DataDirectory'


def get_data_directory():
    """返回安装器配置的数据目录，未配置时使用当前用户的 LocalAppData。"""
    configured_path = os.environ.get('FISHPOOL_DATA_DIR')
    if configured_path:
        return Path(configured_path).expanduser()

    if os.name == 'nt':
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH) as registry_key:
                configured_path, _ = winreg.QueryValueEx(registry_key, REGISTRY_VALUE)
                if configured_path:
                    return Path(configured_path).expanduser()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        return Path(local_app_data) / 'Fishpool'
    return Path.home() / 'AppData' / 'Local' / 'Fishpool'


def get_resource_directory():
    """返回包含打包模板和静态资源的目录，兼容源码与 PyInstaller 运行方式。"""
    packaged_resource_dir = os.environ.get('FISHPOOL_RESOURCE_DIR')
    if packaged_resource_dir:
        return Path(packaged_resource_dir)
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]
