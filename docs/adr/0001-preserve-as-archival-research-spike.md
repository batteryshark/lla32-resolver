# ADR 0001: Preserve LLA32 Resolver as an Archival Research Spike

## Status

Accepted.

## Context

The original project contained a short README, a packed Win32 PE assembly
payload, and a Python script that wrote the payload to disk and executed it.
The project appears to have supported security research and compatibility
patching work where a 64-bit controller needed a 32-bit `LoadLibraryA` address
for a related loader workflow.

Recovered author context: the sidecar process existed because `kernel32.dll`
was expected to be mapped at a stable base address across ordinary processes of
the same bitness during a boot/session. A 32-bit sidecar could resolve the
32-bit `LoadLibraryA` pointer, and a parallel 64-bit sidecar concept could do
the same for 64-bit loader work.

The project is no longer actively developed, but the technique and payload are
worth keeping in a private, navigable repository.

## Decision

Preserve the project as a reference-quality archival artifact instead of
expanding it into a larger injection framework.

The cleanup uses these boundaries:

- Keep the 304-byte payload and assembly source intact as the core artifact.
- Move Python code into a small package with explicit execution.
- Keep the historical `LLA32Resolver` name for recognition.
- Add docs that explain the runtime flow, assumptions, and risks.
- Add tests that validate payload identity without launching the payload.

## Consequences

- Future readers can understand the project without relying on old memory.
- Accidental payload drift is easier to catch.
- The CLI is still available for authorized local research.
- The repo intentionally does not provide a full DLL injection workflow.
- Runtime behavior is less surprising because imports and object construction do
  not execute the payload.

## Reconsider When

- A reproducible assembler toolchain is added and proves the assembly can be
  rebuilt byte-for-byte.
- The payload needs to target a specific documented Windows version matrix.
- The private repository should become a broader collection of related loader
  compatibility research.
