"""
Pre-loads libGLESv2.so.2 into the process before mediapipe is imported.
Required on Render's native Python runtime which lacks this system library.
Imported as the first statement in main.py.
"""
import ctypes
import io
import logging
import subprocess
import tarfile
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

_LIBS_DIR = Path(__file__).parent / "libs"
_GLES_PATH = _LIBS_DIR / "libGLESv2.so.2"

# Candidate URLs — tried in order until one succeeds
_DEB_URLS = [
    # Ubuntu 22.04 (jammy) — Render's OS
    "http://archive.ubuntu.com/ubuntu/pool/main/l/libglvnd/libgles2_1.4.0-1_amd64.deb",
    "http://archive.ubuntu.com/ubuntu/pool/main/l/libglvnd/libgles2_1.4.0-1build1_amd64.deb",
    "http://archive.ubuntu.com/ubuntu/pool/main/l/libglvnd/libgles2_1.4.0-1ubuntu1_amd64.deb",
    # Ubuntu 20.04 (focal) — fallback, stub is ABI-compatible
    "http://archive.ubuntu.com/ubuntu/pool/main/l/libglvnd/libgles2_1.3.2-1~ubuntu0.20.04.1_amd64.deb",
    "http://archive.ubuntu.com/ubuntu/pool/main/l/libglvnd/libgles2_1.3.4-1_amd64.deb",
]

_SYSTEM_SEARCH_PATHS = [
    "/usr/lib/x86_64-linux-gnu/libGLESv2.so.2",
    "/usr/lib/libGLESv2.so.2",
    "/lib/x86_64-linux-gnu/libGLESv2.so.2",
    "/usr/lib/x86_64-linux-gnu/mesa-egl/libGLESv2.so.2",
]


def _try_load(path: str) -> bool:
    try:
        ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)
        return True
    except OSError:
        return False


def _find_on_system() -> str | None:
    for path in _SYSTEM_SEARCH_PATHS:
        if Path(path).exists():
            return path
    try:
        out = subprocess.run(
            ["ldconfig", "-p"], capture_output=True, text=True, timeout=5
        ).stdout
        for line in out.splitlines():
            if "libGLESv2.so.2" in line and "=>" in line:
                return line.split("=>")[-1].strip()
    except Exception:
        pass
    return None


def _extract_so_from_deb(deb_bytes: bytes, dest: Path) -> bool:
    """Pure-Python .deb (ar archive) extractor — no dpkg/ar needed."""
    buf = io.BytesIO(deb_bytes)
    if buf.read(8) != b"!<arch>\n":
        raise ValueError("Not a valid ar archive")

    while True:
        header = buf.read(60)
        if len(header) < 60:
            break
        name = header[:16].decode().strip()
        size = int(header[48:58].decode().strip())
        data = buf.read(size)
        if size % 2:
            buf.read(1)

        if name.startswith("data.tar"):
            with tarfile.open(fileobj=io.BytesIO(data)) as tar:
                for member in tar.getmembers():
                    if "libGLESv2" in member.name:
                        fobj = tar.extractfile(member)
                        if fobj:
                            dest.mkdir(parents=True, exist_ok=True)
                            out = dest / Path(member.name).name
                            out.write_bytes(fobj.read())
                            logger.info("Extracted %s", out)
                            return True
    return False


def ensure_gles() -> None:
    if _try_load("libGLESv2.so.2"):
        return

    path = _find_on_system()
    if path and _try_load(path):
        return

    if _GLES_PATH.exists() and _try_load(str(_GLES_PATH)):
        return

    logger.warning("libGLESv2.so.2 not found — downloading from Ubuntu archive...")
    last_error = None
    for url in _DEB_URLS:
        try:
            logger.info("Trying %s", url)
            with urllib.request.urlopen(url, timeout=30) as resp:
                deb_bytes = resp.read()
            if _extract_so_from_deb(deb_bytes, _LIBS_DIR) and _try_load(str(_GLES_PATH)):
                logger.info("libGLESv2.so.2 loaded from %s", _GLES_PATH)
                return
        except Exception as exc:
            logger.warning("Failed (%s): %s", url, exc)
            last_error = exc

    raise RuntimeError(
        f"Could not load libGLESv2.so.2 from any source. Last error: {last_error}"
    )


ensure_gles()
