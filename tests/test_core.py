import subprocess
import unittest

from api_contract_inspector.core import InspectionError, inspect

BASE = '{"openapi":"3.0.3","info":{"title":"Example","version":"1"},"paths":{}}'


class FakeResult:
    returncode = 0
    stdout = "## Changed endpoints\n"
    stderr = ""


class ContractInspectorTests(unittest.TestCase):
    def test_valid_compare_and_safe_flags(self):
        recorded = []

        def run(command, **kwargs):
            recorded.append((command, kwargs))
            return FakeResult()

        self.assertEqual(inspect(BASE, BASE, runner=run), "## Changed endpoints")
        self.assertEqual(recorded[0][0][1], "changelog")
        self.assertIn("--allow-external-refs=false", recorded[0][0])
        self.assertEqual(recorded[0][1]["timeout"], 12)

    def test_rejects_empty_large_and_invalid_modes(self):
        with self.assertRaises(InspectionError):
            inspect("", BASE)
        with self.assertRaises(InspectionError):
            inspect(BASE * 10000, BASE)
        with self.assertRaises(InspectionError):
            inspect(BASE, BASE, mode="execute")

    def test_handles_missing_upstream_binary(self):
        def missing(_command, **_kwargs):
            raise FileNotFoundError("oasdiff")
        with self.assertRaisesRegex(InspectionError, "not installed"):
            inspect(BASE, BASE, runner=missing)

    def test_handles_timeout_without_exposing_input(self):
        def stuck(_command, **_kwargs):
            raise subprocess.TimeoutExpired(cmd="oasdiff", timeout=12)
        with self.assertRaisesRegex(InspectionError, "time limit"):
            inspect(BASE, BASE, runner=stuck)


if __name__ == "__main__":
    unittest.main()
