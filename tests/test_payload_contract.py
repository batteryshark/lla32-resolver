from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from lla32_resolver.payload import (
    EXIT_PROCESS_HASH,
    LLA32_PAYLOAD,
    LOAD_LIBRARY_A_HASH,
    PAYLOAD_SHA256,
    PAYLOAD_SIZE,
    matches_export_hash,
    payload_sha256,
)
from lla32_resolver.resolver import LLA32Resolver, _normalize_exit_code


class PayloadContractTests(unittest.TestCase):
    def test_payload_size_matches_archival_fingerprint(self) -> None:
        self.assertEqual(len(LLA32_PAYLOAD), PAYLOAD_SIZE)

    def test_payload_sha256_matches_archival_fingerprint(self) -> None:
        self.assertEqual(payload_sha256(), PAYLOAD_SHA256)

    def test_payload_starts_with_packed_mz_and_pe_headers(self) -> None:
        self.assertEqual(LLA32_PAYLOAD[0:2], b"MZ")
        self.assertEqual(LLA32_PAYLOAD[4:8], b"PE\0\0")

    def test_load_library_seed_matches_export_name(self) -> None:
        self.assertTrue(matches_export_hash(LOAD_LIBRARY_A_HASH, "LoadLibraryA"))

    def test_exit_process_seed_matches_export_name(self) -> None:
        self.assertTrue(matches_export_hash(EXIT_PROCESS_HASH, "ExitProcess"))

    def test_export_seed_does_not_match_other_name(self) -> None:
        self.assertFalse(matches_export_hash(LOAD_LIBRARY_A_HASH, "ExitProcess"))

    def test_exit_code_is_normalized_as_dword(self) -> None:
        self.assertEqual(_normalize_exit_code(-1), 0xFFFFFFFF)

    def test_resolver_construction_does_not_execute_payload(self) -> None:
        self.assertIsNone(LLA32Resolver().address)


if __name__ == "__main__":
    unittest.main()
