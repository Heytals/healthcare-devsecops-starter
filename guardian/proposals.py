
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "security-findings.json"
PROPOSALS = ROOT / "reports" / "remediation-proposals.json"

# These are review suggestions, not automatic Terraform edits.
GUIDANCE = {
    "CKV2_AWS_62": {
        "risk": "Monitoring gap",
        "action": (
            "Review which S3 object events need monitoring, then propose "
            "an event-notification destination and required permissions."
        ),
        "approval": "Cloud administrator and monitoring owner",
    },
    "CKV_AWS_144": {
        "risk": "Recovery and resilience gap",
        "action": (
            "Review recovery objectives, destination region, replication "
            "permissions, and expected storage/transfer costs before "
            "proposing cross-region replication."
        ),
        "approval": "Cloud administrator and data owner",
    },
    "CKV2_AWS_61": {
        "risk": "Data lifecycle policy missing",
        "action": (
            "Define retention and deletion requirements for this bucket, "
            "then propose a lifecycle policy consistent with those rules."
        ),
        "approval": "Data owner and security administrator",
    },
    "CKV2_AWS_64": {
        "risk": "Encryption key policy needs review",
        "action": (
            "Review the KMS key policy to ensure only approved roles "
            "can administer the key and use it for encryption/decryption."
        ),
        "approval": "Cloud security administrator",
    },
}


def main():
    if not REPORT.exists():
        raise SystemExit(
            "Scan report not found. Run guardian\\scanner.py first."
        )

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    findings = report.get("findings", {})
    results = findings.get("results", {})
    failed_checks = results.get("failed_checks", [])

    proposals = []
    for finding in failed_checks:
        check_id = finding.get("check_id", "UNKNOWN")
        guidance = GUIDANCE.get(check_id)

        if guidance is None:
            guidance = {
                "risk": "Unclassified security finding",
                "action": (
                    "Review the scanner's finding and official guidance "
                    "before preparing a change."
                ),
                "approval": "Security administrator",
            }

        proposals.append({
            "proposal_id": f"PROP-{len(proposals) + 1:03d}",
            "check_id": check_id,
            "check_name": finding.get("check_name"),
            "resource": finding.get("resource"),
            "file_path": finding.get("file_path"),
            "guideline": finding.get("guideline"),
            "risk_category": guidance["risk"],
            "proposed_action": guidance["action"],
            "approval_required_from": guidance["approval"],
            "status": "pending_review",
            "infrastructure_changed": False,
        })

    output = {
        "product": "Healthcare Cloud Security Guardian",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": "security-findings.json",
        "mode": "proposal_only",
        "automatic_changes_enabled": False,
        "proposal_count": len(proposals),
        "proposals": proposals,
    }

    PROPOSALS.parent.mkdir(parents=True, exist_ok=True)
    PROPOSALS.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print(f"Proposals generated: {len(proposals)}")
    print(f"Saved to: {PROPOSALS}")
    print("Status: pending_review")
    print("Infrastructure changed: NO")


if __name__ == "__main__":
    main()
