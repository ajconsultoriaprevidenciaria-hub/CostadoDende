import os
import runpy
import shutil
import sys
import threading
import webbrowser
from pathlib import Path


def _bundle_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _runtime_dir() -> Path:
    base_dir = Path(os.getenv('LOCALAPPDATA', Path.home()))
    runtime_dir = base_dir / 'CostadoDende'
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir


def _copy_if_missing(source: Path, target: Path) -> None:
    if not source.exists() or target.exists():
        return
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def prepare_runtime() -> Path:
    bundle_dir = _bundle_dir()
    runtime_dir = _runtime_dir()

    _copy_if_missing(bundle_dir / 'db.sqlite3', runtime_dir / 'db.sqlite3')
    _copy_if_missing(bundle_dir / 'media', runtime_dir / 'media')

    os.environ.setdefault('COSTADODENDE_RUNTIME_DIR', str(runtime_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    return runtime_dir


def open_browser() -> None:
    webbrowser.open('http://127.0.0.1:8000/')


def main() -> None:
    bundle_dir = _bundle_dir()
    prepare_runtime()

    threading.Timer(2.0, open_browser).start()
    os.chdir(bundle_dir)
    sys.path.insert(0, str(bundle_dir))
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
    runpy.run_path(str(bundle_dir / 'manage.py'), run_name='__main__')


if __name__ == '__main__':
    main()