
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_SCRIPT = PROJECT_ROOT / "guardian" / "review.py"


class ReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

        self.reports = self.root / "reports"
        self.reports.mkdir()

        self.proposals_file = self.reports / "remediation-proposals.json"
        self.audit_file = self.reports / "review-audit.jsonl"
        self.state_file = self.reports / "review-state.json"

        self.proposals_file.write_text(
            json.dumps({
                "proposals": [
                    {"proposal_id": "PROP-TEST-001", "status": "pending_review"},
                    {"proposal_id": "PROP-TEST-002", "status": "pending_review"},
                ]
            }),
            encoding="utf-8",
        )

    def run_review(self, proposal_id, decision="approve"):
        # Run the real script while redirecting its data files to a
        # temporary directory, so tests never touch your local reports.
        bootstrap = r"""
import runpy
import sys
from pathlib import Path

root = Path(sys.argv[1])
script = Path(sys.argv[2])

import runpy as runner
import sys as system

# Redirect the review script's module-level file paths before main runs.
source = script.read_text(encoding="utf-8")
source = source.replace(
    'ROOT = Path(__file__).resolve().parent.parent',
    f'ROOT = Path({str(Path(sys.argv[1]).as_posix())!r})'
)
exec(compile(source, str(script), "exec"), {"__name__": "__main__", "__file__": str(script)})
"""
        # Simpler and more reliable test seam: use a temporary copy of the
        # script with its project root redirected.
        test_script = self.root / "review_under_test.py"
        source = REVIEW_SCRIPT.read_text(encoding="utf-8")
        source = source.replace(
            'ROOT = Path(__file__).resolve().parent.parent',
            f'ROOT = Path({str(self.root)!r})',
        )
        test_script.write_text(source, encoding="utf-8")

        return subprocess.run(
            [
                sys.executable,
                str(test_script),
                proposal_id,
                decision,
                "--reviewer",
                "Automated Test Reviewer",
                "--note",
                "Unit test",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_approval_records_state_and_does_not_execute_fix(self):
        result = self.run_review("PROP-TEST-001", "approve")

        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.assertEqual(state["PROP-TEST-001"]["status"], "approved")

        audit = self.audit_file.read_text(encoding="utf-8")
        event = json.loads(audit.strip().splitlines()[-1])
        self.assertFalse(event["infrastructure_changed"])
        self.assertEqual(event["execution_status"], "not_executed")

    def test_rejection_records_rejected_status(self):
        result = self.run_review("PROP-TEST-002", "reject")

        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.assertEqual(state["PROP-TEST-002"]["status"], "rejected")

    def test_duplicate_review_is_blocked(self):
        first = self.run_review("PROP-TEST-001", "approve")
        second = self.run_review("PROP-TEST-001", "reject")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("already has a review decision", second.stderr)

    def test_unknown_proposal_is_rejected(self):
        result = self.run_review("PROP-DOES-NOT-EXIST", "approve")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Proposal not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
