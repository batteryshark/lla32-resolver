"""Command-line entrypoint for LLA32 Resolver."""

from __future__ import annotations

import sys

from .resolver import LLA32ResolverError, resolve_load_library_a


def main() -> int:
    try:
        address = resolve_load_library_a()
    except LLA32ResolverError as exc:
        print(f"lla32-resolver: {exc}", file=sys.stderr)
        return 1

    print(f"LoadLibraryA Address [WIN32]: 0x{address:08X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
