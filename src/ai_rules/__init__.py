from importlib import metadata
from pathlib import Path

try:
    __version__ = metadata.version("ai-rules")
except metadata.PackageNotFoundError:
    __version__ = (Path(__file__).resolve().parents[2] / "VERSION").read_text().strip()
