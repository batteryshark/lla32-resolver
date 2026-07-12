"""Compatibility entrypoint for the historical root-level script.

New code should import from ``lla32_resolver`` after installing the package.
This file remains so ``python __init__.py`` still runs the archival CLI from a
fresh checkout.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = PROJECT_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from lla32_resolver.__main__ import main


if __name__ == "__main__":
    raise SystemExit(main())
