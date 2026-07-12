# Development

## Requirements

- Python 3.10 or newer.
- Windows if you intend to execute the resolver payload.
- Optional: `yasm` or `nasm` if you want to rebuild the flat binary payload from
  [payload/lla32_payload.asm](payload/lla32_payload.asm).

## Setup

```powershell
python -m pip install -e .
```

## Test

```powershell
python -m unittest discover -s tests
```

The tests do not execute the payload. They verify the embedded bytes, export
hash seeds, return-code normalization, and non-executing resolver behavior.

## Run

```powershell
python -m lla32_resolver
```

or, after installation:

```powershell
lla32-resolve
```

Running either command writes the embedded PE bytes to a temporary executable,
starts it as a child process, reads its exit code, and removes the temporary
file.

## Payload Rebuild Notes

The historical comment says this was originally built with `yasm`. On a machine
with an assembler installed, the intended shape is a flat binary:

```powershell
yasm -f bin -o build\lla32_payload.bin payload\lla32_payload.asm
```

or:

```powershell
nasm -f bin -o build\lla32_payload.bin payload\lla32_payload.asm
```

The rebuilt file should be exactly `304` bytes and match this SHA-256:

```text
03d4fa4ac71e696568f08c0c5c8a0fedccfb4bb14ad60e24a2b2ca15b3241ff1
```

If the bytes change, update [src/lla32_resolver/payload.py](src/lla32_resolver/payload.py)
and the tests in the same commit, with a note explaining why the payload changed.

## Safe Change Rules

- Treat [payload/lla32_payload.asm](payload/lla32_payload.asm) as the historical
  artifact.
- Do not refactor the assembly only for style unless you can rebuild and compare
  the payload bytes.
- Keep runtime execution explicit. Imports and object construction should not
  launch the payload.
- Preserve temporary-file cleanup on every execution path.
- Keep tests fast and non-executing by default.
