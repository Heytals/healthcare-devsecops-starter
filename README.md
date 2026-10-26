# Healthcare Cloud Security Guardian

**Automated infrastructure security scanning, risk reporting, and human-reviewed remediation proposals for healthcare cloud environments.**

[![Infrastructure Security Checks](https://github.com/Heytals/healthcare-devsecops-starter/actions/workflows/security.yml/badge.svg)](https://github.com/Heytals/healthcare-devsecops-starter/actions/workflows/security.yml)

## Overview

Healthcare Cloud Security Guardian is a DevSecOps prototype that demonstrates how infrastructure security checks can be integrated into a continuous integration pipeline. It scans Terraform examples, evaluates selected security controls, generates machine-readable findings, and prepares remediation proposals for human review.

The project is designed to demonstrate a security workflow without requiring an AWS account or deploying cloud resources.

## Problem Statement

Cloud infrastructure misconfigurations can expose sensitive healthcare information, weaken access controls, or undermine data protection. Manually reviewing every infrastructure change can be time-consuming and inconsistent.

Guardian demonstrates an automated approach to detecting selected infrastructure risks early in the development process and preparing findings for security staff to review.

## Key Features

- **Infrastructure security scanning:** Uses Checkov to scan Terraform configuration.
- **CI security gates:** GitHub Actions runs mandatory checks against the secure example.
- **Negative testing:** An intentionally insecure example is expected to fail the configured security checks.
- **Automated findings:** Generates `security-findings.json`.
- **Remediation proposals:** Generates `remediation-proposals.json` with proposals awaiting review.
- **Human-review prototype:** Records local approval and rejection decisions, including reviewer-supplied information and timestamps.
- **Duplicate-review protection:** Blocks a second decision for a proposal that already has a recorded decision.
- **Audit records:** Stores local review events and a separate current review-state snapshot.
- **Automated tests:** Python `unittest` tests cover approval, rejection, duplicate-review blocking, and unknown proposal IDs.

## Architecture

```text
Developer pushes code
        |
        v
GitHub Actions workflow
        |
        +--> Mandatory Terraform security checks
        |
        +--> Negative test for insecure configuration
        |
        +--> Guardian report generation
        |        |
        |        +--> security-findings.json
        |        +--> remediation-proposals.json
        |
        +--> Automated review unit tests

Local reviewer
        |
        v
guardian/review.py
        |
        +--> review-audit.jsonl
        +--> review-state.json
        |
        v
Decision recorded; no infrastructure changes executed
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Terraform | Infrastructure as Code examples |
| Checkov | Static infrastructure security scanning |
| Python 3.11 | Guardian scripts and automated tests |
| GitHub Actions | Automated CI workflow |
| Git and GitHub | Version control and source hosting |
| JSON / JSON Lines | Findings, proposals, review state, and audit events |

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── security.yml
├── custom_checks/
├── examples/
│   ├── secure/
│   └── insecure/
├── guardian/
│   ├── scanner.py
│   ├── proposals.py
│   └── review.py
├── tests/
│   └── test_review.py
├── presentation/
├── report/
├── .gitignore
├── DEMO_CHECKLIST.md
├── SECURITY_GATE_NOTES.md
└── README.md
```

Runtime reports are generated locally or uploaded as GitHub Actions artifacts. Their contents may vary with the configuration and scan results.

## Prerequisites

- Git
- Python 3.11 recommended
- VS Code or another text editor
- A GitHub account to run the hosted workflow

Terraform CLI is optional for additional Terraform validation. Scanning the examples does not require AWS credentials.

## Run Locally

### 1. Create and activate a virtual environment

From the repository root on Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Checkov

```bat
python -m pip install --upgrade pip
python -m pip install checkov==3.3.29
checkov --version
```

### 3. Run the Guardian scanner

```bat
python guardian\scanner.py
```

This generates `reports/security-findings.json`. The script reports that infrastructure was not changed.

### 4. Generate remediation proposals

```bat
python guardian\proposals.py
```

This generates `reports/remediation-proposals.json`. Proposals are intended for review; generating them does not apply fixes.

### 5. Run the automated tests

```bat
python -m unittest discover -s tests -v
```

The current review test suite covers four cases: approval, rejection, duplicate-review blocking, and unknown proposal IDs.

### 6. Record a review decision

Use a proposal ID that exists in the generated proposal report and has not already been reviewed.

Approve a proposal:

```bat
python guardian\review.py PROP-001 approve --reviewer "Security Reviewer" --note "Reviewed for the demo"
```

Reject a proposal:

```bat
python guardian\review.py PROP-002 reject --reviewer "Security Reviewer" --note "Needs further analysis"
```

Replace the example IDs with eligible proposal IDs from your report. Each proposal can receive only one recorded decision in the current implementation.

Review data is stored in:

- `reports/review-audit.jsonl` — appended review events.
- `reports/review-state.json` — the current status snapshot.

**Important:** These commands record decisions only. They do not apply infrastructure changes.

## GitHub Actions

The workflow at `.github/workflows/security.yml` runs on pushes to `main` and on pull requests.

It includes four jobs:

1. **Mandatory security gate:** Scans the secure Terraform example against selected Checkov controls.
2. **Negative test:** Verifies that the intentionally insecure example is rejected by the configured checks.
3. **Guardian reporting:** Generates findings and remediation proposals, then uploads JSON reports as an artifact.
4. **Unit tests:** Runs the Python review tests using `unittest`.

A successful workflow means the configured checks and tests passed. It does not establish that every security risk has been detected.

## Demo Walkthrough

1. Show the secure and intentionally insecure Terraform examples.
2. Run Checkov against the insecure example and explain the findings.
3. Open GitHub Actions and show the passing workflow.
4. Download the `guardian-security-reports` artifact and inspect both JSON files.
5. Show a remediation proposal in `pending_review` status.
6. Record an approval or rejection using `guardian/review.py`.
7. Inspect `review-audit.jsonl` and `review-state.json`.
8. Run the unit tests and show the four passing cases.

Use synthetic examples only. Do not include real patient information.

## Security and Compliance Limitations

This repository is an educational prototype, not a production security platform or certified healthcare-compliance solution.

- It does not deploy infrastructure by default.
- It does not independently prove HIPAA or other regulatory compliance.
- The review CLI accepts a reviewer-supplied name; it does not authenticate the reviewer's identity.
- Review state and audit files are local demo records, not tamper-proof or transaction-safe enterprise audit storage.
- The current review tool does not apply proposed fixes or deploy approved changes.
- Checkov only evaluates the controls and configuration it is given; a passing scan is not proof that a system is secure.
- The demo does not provide a live background monitoring service for a connected cloud account.

Never use real patient data or production credentials in this demo.

## Future Enhancements

- Authenticated reviewer identities and role-based access control.
- A web-based review dashboard.
- Atomic, concurrency-safe decisions and tamper-evident audit storage.
- More comprehensive automated tests and policy coverage.
- Reviewable patch generation with explicit approval before any execution.
- Optional cloud integrations with least-privilege access and clear cost controls.
- Monitoring and alerting for supported cloud environments.
- Compliance evidence mapping reviewed by qualified security and compliance professionals.

## Project Status

**Current status:** Working CI prototype with automated Terraform security checks, JSON findings and remediation proposals, a local review/audit mechanism, and automated review unit tests.

**Deployment status:** No live cloud deployment is performed by the current workflow.

---

Built as a learning and demonstration project for healthcare cloud infrastructure security and DevSecOps.
