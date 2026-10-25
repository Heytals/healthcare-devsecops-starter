
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORT_DIR / "security-findings.json"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable, "-m", "checkov.main",
        "-d", str(PROJECT_ROOT / "examples" / "secure"),
        "--framework", "terraform",
        "--output", "json",
        "--quiet",
    ]

    print("Healthcare Cloud Security Guardian")
    print("Scanning secure Terraform example...")

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: Security scan timed out.")
        return 2

    if result.returncode not in (0, 1):
        print("ERROR: Checkov could not complete the scan.")
        print(result.stderr[-2000:])
        return 2

    try:
        findings = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("ERROR: Checkov did not return valid JSON.")
        print(result.stderr[-2000:])
        return 2

    report = {
        "product": "Healthcare Cloud Security Guardian",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_target": "examples/secure",
        "mode": "report_only",
        "infrastructure_changed": False,
        "scan_exit_code": result.returncode,
        "findings": findings,
        "remediation": {
            "status": "not_generated",
            "message": (
                "No fixes have been applied. Proposed fixes require "
                "a separate review and approval workflow."
            ),
        },
    }

    REPORT_FILE.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(f"Report saved to: {REPORT_FILE}")
    print("Infrastructure changed: NO")
    print("Remediation mode: proposal-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
