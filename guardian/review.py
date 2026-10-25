
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"
PROPOSALS_FILE = REPORTS_DIR / "remediation-proposals.json"
AUDIT_FILE = REPORTS_DIR / "review-audit.jsonl"
STATE_FILE = REPORTS_DIR / "review-state.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_audit():
    events = []
    if not AUDIT_FILE.exists():
        return events

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid audit JSON on line {number}"
                ) from exc

            if not isinstance(event, dict):
                raise ValueError(f"Invalid audit event on line {number}")
            events.append(event)

    return events


def main():
    parser = argparse.ArgumentParser(
        description="Record a Guardian proposal review decision."
    )
    parser.add_argument("proposal_id", help="Example: PROP-003")
    parser.add_argument("decision", choices=["approve", "reject"])
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    reviewer = args.reviewer.strip()
    if not reviewer:
        parser.error("--reviewer cannot be blank")

    if not PROPOSALS_FILE.exists():
        parser.error(
            "Proposal report not found; run guardian\\proposals.py first.")

    try:
        report = read_json(PROPOSALS_FILE)
        audit = load_audit()
        state = read_json(STATE_FILE) if STATE_FILE.exists() else {}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(f"Could not safely read review data: {exc}")

    proposals = report.get("proposals", [])
    proposal = next(
        (p for p in proposals if p.get("proposal_id") == args.proposal_id),
        None,
    )
    if proposal is None:
        parser.error(f"Proposal not found: {args.proposal_id}")

    # Existing audit entries also count, so older decisions remain protected.
    previous = next(
        (e for e in audit if e.get("proposal_id") == args.proposal_id),
        None,
    )
    if previous is not None or args.proposal_id in state:
        parser.error(f"{args.proposal_id} already has a review decision.")

    if proposal.get("status") != "pending_review":
        parser.error(
            "Only proposals with pending_review status can be reviewed.")

    timestamp = datetime.now(timezone.utc).isoformat()
    event = {
        "proposal_id": args.proposal_id,
        "decision": args.decision,
        "reviewer": reviewer,
        "note": args.note,
        "reviewed_at": timestamp,
        "infrastructure_changed": False,
        "execution_status": "not_executed",
    }

    # Prepare state and append the audit event before writing the state snapshot.
    new_state = dict(state)
    new_state[args.proposal_id] = {
        "decision": args.decision,
        "status": "approved" if args.decision == "approve" else "rejected",
        "reviewer": reviewer,
        "reviewed_at": timestamp,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")

        STATE_FILE.write_text(
            json.dumps(new_state, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        parser.error(
            f"Could not save review data: {exc}. "
            "Check the audit log before retrying."
        )

    print(f"Proposal: {args.proposal_id}")
    print(f"Decision: {args.decision}")
    print(f"Status: {new_state[args.proposal_id]['status']}")
    print(f"Reviewer: {reviewer}")
    print("Audit event recorded.")
    print("Infrastructure changed: NO")
    print("Fix executed: NO")


if __name__ == "__main__":
    main()
