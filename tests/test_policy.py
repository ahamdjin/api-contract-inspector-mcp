import json
import unittest

from api_contract_inspector.policy import decode_oasdiff_json, review_policy
from api_contract_inspector.core import inspect, InspectionError

BASE='{"openapi":"3.0.3","info":{"title":"Demo","version":"1"},"paths":{}}'

class ExitOne:
    returncode=1
    stdout='[{"id":"api-path-removed-without-deprecation","text":"api path removed","level":3,"operation":"GET","path":"/old"}]'
    stderr=''

class PolicyTests(unittest.TestCase):
    def test_exit_one_with_structured_results_is_data(self):
        value=inspect(BASE,BASE,mode="breaking",format="json",runner=lambda *_a,**_k:ExitOne())
        findings=decode_oasdiff_json(value)
        self.assertEqual(findings[0]["id"],"api-path-removed-without-deprecation")

    def test_release_gate_and_named_human_accepted_rule(self):
        findings=decode_oasdiff_json(ExitOne.stdout)
        blocked=review_policy(findings)
        self.assertEqual(blocked["summary"]["blocked"],1)
        self.assertEqual(blocked["decision"],"review-required")
        accepted=review_policy(findings,accepted_rules=["api-path-removed-without-deprecation"])
        self.assertEqual(accepted["summary"]["blocked"],0)
        self.assertEqual(accepted["summary"]["accepted"],1)

    def test_no_false_clean_result_for_invalid_oasdiff_json(self):
        with self.assertRaises(ValueError):
            decode_oasdiff_json('{"error": "not findings"}')
        with self.assertRaises(InspectionError):
            inspect(BASE,BASE,mode="breaking",format="json",
                    runner=lambda *_a,**_k: type("Result",(),{"returncode":1,"stdout":"invalid","stderr":""})())

    def test_policy_rejects_unexpected_whitelist_types(self):
        with self.assertRaises(ValueError):
            review_policy([],accepted_rules="danger")
        with self.assertRaises(ValueError):
            review_policy([{"id":"x","level":"3"}])

if __name__=="__main__":
    unittest.main()
