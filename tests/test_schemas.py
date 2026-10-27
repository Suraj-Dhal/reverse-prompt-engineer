"""Validate the eval fixtures against their JSON Schemas (skipped if jsonschema is not installed)."""
from __future__ import annotations

import json
import unittest

from _support import ROOT

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency
    jsonschema = None

FIXTURES = ROOT / "evals" / "fixtures"


@unittest.skipIf(jsonschema is None, "pip install jsonschema to run schema tests")
class FixtureSchemas(unittest.TestCase):
    def check(self, data_name, schema_name):
        data = json.loads((FIXTURES / data_name).read_text(encoding="utf-8"))
        schema = json.loads((FIXTURES / "schema" / schema_name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        self.assertEqual([f"{list(e.path)}: {e.message}" for e in errors], [])

    def test_trigger_fixtures(self):
        self.check("trigger-evals.json", "trigger-evals.schema.json")

    def test_reconstruction_fixtures(self):
        self.check("reconstruction-evals.json", "reconstruction-evals.schema.json")


if __name__ == "__main__":
    unittest.main()
