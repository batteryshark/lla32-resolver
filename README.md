# LLA32 Resolver

LLA32 Resolver is an archival Windows research spike for recovering the
32-bit `kernel32!LoadLibraryA` address from a helper process. It preserves a
304-byte, hand-packed Win32 PE payload and a small Python wrapper that writes
that payload to a temporary executable, runs it, and reads the payload's result
from the process exit code.

This repository is kept for security research, compatibility patching, and
historical reference. It is not an actively maintained injection framework.

## Current Status

- Classification: keep as a reference-quality archival research project.
- Runtime target: Windows with 32-bit process execution support.
- Payload source: [payload/lla32_payload.asm](payload/lla32_payload.asm).
- Python API: [src/lla32_resolver](src/lla32_resolver).
- Tests: non-executing contract tests for payload identity and resolver helpers.

The embedded payload is intentionally fingerprinted:

- Size: `304` bytes
- SHA-256: `03d4fa4ac71e696568f08c0c5c8a0fedccfb4bb14ad60e24a2b2ca15b3241ff1`

## Quick Start

Install from the checkout:

```powershell
python -m pip install -e .
```

Run the non-executing tests:

```powershell
python -m unittest discover -s tests
```

Resolve the 32-bit `LoadLibraryA` address on Windows:

```powershell
python -m lla32_resolver
```

The CLI executes the preserved payload in a child process. Do that only in a
controlled, authorized research environment.

## Repository Map

```text
.
|-- README.md
|-- ARCHITECTURE.md
|-- DEVELOPMENT.md
|-- pyproject.toml
|-- __init__.py
|-- payload/
|   `-- lla32_payload.asm
|-- src/
|   `-- lla32_resolver/
|       |-- __init__.py
|       |-- __main__.py
|       |-- payload.py
|       `-- resolver.py
|-- tests/
|   `-- test_payload_contract.py
`-- docs/
    `-- adr/
        `-- 0001-preserve-as-archival-research-spike.md
```

The root-level `__init__.py` is retained only as a compatibility CLI for the
old `python __init__.py` workflow. New code should import the package from
`src/lla32_resolver`.

## What It Does

The payload walks the 32-bit process environment block, finds the loaded
`kernel32.dll` module, resolves exports using the original xor-and-rotate hash
loop, and exits through `ExitProcess` with the resolved `LoadLibraryA` pointer
as the process exit code. The Python wrapper normalizes that exit code as a
32-bit unsigned value.

The historical operating idea was that Windows maps `kernel32.dll` at a stable
base address across ordinary processes of the same bitness during a boot/session.
A sidecar process could therefore resolve the 32-bit or 64-bit `LoadLibraryA`
address in its own virtual address space, and the loader could reuse that
same-bitness address in the target process.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system map, data flow, and
load-bearing assumptions.
