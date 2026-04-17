"""
Pre-loads libGLESv2.so.2 into the process before mediapipe is imported.
Required on Render's native Python runtime which lacks this system library.
Imported as the first statement in main.py.
"""
import ctypes
import io
import logging
import tarfile
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

_LIBS_DIR = Path(__file__).parent / "libs"
_GLES_PATH = _LIBS_DIR / "libGLESv2.so.2"
# libgles2 1.4.0-1 from Ubuntu 22.04 (jammy) — matches Render's OS
_DEB_URL = (
    "http://archive.ubuntu.com/ubuntu/pool/main/l/libglvnd/"
    "libgles2_1.4.0-1_amd64.deb"
)


def _try_load(path: str) -> bool:
    try:
        ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)
        return True
    except OSError:
        return False


def _extract_so_from_deb(deb_bytes: bytes, dest: Path) -> None:
    """Pure-Python .deb extractor — no ar/dpkg-deb needed."""
    f = io.BytesIO(deb_bytes)
    assert f.read(8) == b"!<arch>\n", "Not a valid ar archive"

    while True:
        header = f.read(60)
        if len(header) < 60:
            break
        name = header[:16].decode().strip()
        size = int(header[48:58].decode().strip())
        data = f.read(size)
        if size % 2:
            f.read(1)

        if name.startswith("data.tar"):
            with tarfile.open(fileobj=io.BytesIO(data)) as tar:
                for member in tar.getmembers():
                    if "libGLESv2" in member.name:
                        extracted = tar.extractfile(member)
                        if extracted:
                            dest.mkdir(parents=True, exist_ok=True)
                            out = dest / Path(member.name).name
                            out.write_bytes(extracted.read())
                            logger.info("Extracted %s", out)
            return

    raise RuntimeError("data.tar not found in .deb archive")


def ensure_gles() -> None:
    if _try_load("libGLESv2.so.2"):
        return

    if _GLES_PATH.exists() and _try_load(str(_GLES_PATH)):
        return

    logger.warning("libGLESv2.so.2 not found — downloading from Ubuntu archive...")
    deb_bytes, _ = urllib.request.urlretrieve(_DEB_URL)
    _extract_so_from_deb(Path(deb_bytes).read_bytes(), _LIBS_DIR)

    if not _try_load(str(_GLES_PATH)):
        raise RuntimeError(f"Failed to load libGLESv2.so.2 from {_GLES_PATH}")

    logger.info("libGLESv2.so.2 loaded successfully from %s", _GLES_PATH)


ensure_gles()
