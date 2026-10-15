"""Empaqueta únicamente los archivos públicos que necesita la PWA."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist"
FILES = ["index.html", "sw.js", "manifest.webmanifest"]
DIRECTORIES = ["assets", "books", "controller", "data", "model", "vendor", "view"]

if __name__ == "__main__":
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / name, DEST / name)
    for name in DIRECTORIES:
        shutil.copytree(ROOT / name, DEST / name)
    (DEST / ".nojekyll").touch()
    print(f"Sitio empaquetado en {DEST}")
