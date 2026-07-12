# Architecture

## Purpose

LLA32 Resolver preserves a small cross-bitness research technique: launch a
32-bit helper payload, let that helper resolve `kernel32!LoadLibraryA` inside
its own 32-bit address space, and report the pointer value back to Python.

The recovered design intent was sidecar address discovery. The broader loader
workflow could launch a helper matching the target bitness, resolve
`LoadLibraryA` from that helper's virtual address space, and then reuse the
result when building the target-side loader state. This relied on the historical
Windows behavior that system DLLs such as `kernel32.dll` were mapped at stable
base addresses across ordinary processes of the same bitness during a
boot/session.

The project is archival. The main design goal is making the old payload easy to
understand and verify without casually changing bytes that were packed around
PE header layout constraints.

## System Map

```text
User / script
    |
    v
Python CLI or API
    |
    | writes embedded payload to a temporary .exe
    v
32-bit PE payload child process
    |
    | walks PEB loader lists and kernel32 export table
    v
ExitProcess(exit_code = LoadLibraryA address)
    |
    v
Python normalizes DWORD exit code and returns an int
```

## Components

| Component | Responsibility | Confidence |
| --- | --- | --- |
| `src/lla32_resolver/resolver.py` | Windows/platform boundary, temporary executable lifecycle, subprocess execution, exit-code normalization. | High |
| `src/lla32_resolver/payload.py` | Embedded 304-byte payload, payload fingerprint, export hash matcher used by tests and documentation. | High |
| `payload/lla32_payload.asm` | Historical assembly source for the packed Win32 PE payload. | High |
| `tests/test_payload_contract.py` | Fast tests that validate payload identity and helper behavior without executing the payload. | High |
| `docs/adr/0001-preserve-as-archival-research-spike.md` | Durable rationale for preserving this as a reference project rather than expanding it. | High |

## Runtime Flow

1. `resolve_load_library_a()` verifies the host is Windows.
2. Python writes `LLA32_PAYLOAD` to a named temporary `.exe`.
3. Python launches that file as a child process.
4. The payload walks `fs:[0x30]` to reach the 32-bit PEB and loader data.
5. The payload follows the loader list entries to the module assumed to be
   `kernel32.dll`.
6. The export resolver scans named exports and applies the historical
   xor-and-rotate loop until the seed collapses to zero.
7. The payload jumps to `ExitProcess` with the resolved `LoadLibraryA` address
   positioned as the process exit code.
8. Python masks the subprocess return code to a 32-bit unsigned integer.
9. Python deletes the temporary executable in a `finally` block.

## Load-Bearing Weirdness

- The useful address is same-bitness. A 32-bit helper resolves the 32-bit
  `kernel32!LoadLibraryA` address; a separate 64-bit helper would be needed for
  the 64-bit address.
- The payload is a sectionless PE with code placed inside header slack. That is
  intentional size work, not ordinary application layout.
- The assembly relies on the 32-bit TEB/PEB structure and loader list order that
  was common for the target Windows era.
- The export resolver seed values are not normal hashes. They are starting
  states that become zero after processing the target export name plus the
  terminating NUL byte.
- `ExitProcess` is reached by `jmp`, not `call`; the payload shapes the stack so
  the `LoadLibraryA` pointer is read as the exit code.
- There are two export resolver blocks in the assembly. That duplication is
  preserved because the payload is packed into PE header gaps and has not been
  reassembled during this cleanup.

## Known Weaknesses

- A process exit code is a brittle transport for pointer values. It works for
  32-bit values, but callers must treat the result as a DWORD and not a normal
  success/failure code.
- The helper reports the address in the helper process, not in an arbitrary
  target process. That was useful only when same-bitness system DLL layout
  assumptions held for the target environment.
- The repository does not currently include a reproducible assembler check
  because `yasm`/`nasm` was not available during cleanup.
- Running the CLI executes a raw PE payload. Tests intentionally avoid doing
  that.

## Comprehensibility Scorecard

| Dimension | Score | Evidence |
| --- | ---: | --- |
| Onboarding clarity | 8/10 | README now states purpose, status, repository map, and safe run path. |
| Execution discoverability | 8/10 | CLI, package entrypoint, and compatibility root script are documented. |
| Architecture coherence | 8/10 | Runtime flow and payload assumptions are centralized here. |
| Data-flow clarity | 8/10 | The temp-exe and exit-code path is explicit. |
| Decision documentation | 7/10 | One ADR captures the preservation stance; deeper OS-version rationale is still historical memory. |
| Test trust | 6/10 | Tests protect payload identity and pure helpers, but do not execute the payload. |
| Change safety | 7/10 | Payload fingerprint and load-bearing notes reduce accidental byte drift. |

Overall: `7.4/10`. The next meaningful improvement would be a reproducible
assembler check on a machine with `yasm` or `nasm`.
