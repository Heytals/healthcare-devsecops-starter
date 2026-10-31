# Project Report: Healthcare Cloud Security Guardian

**Project category:** Cloud Security, DevSecOps, and Infrastructure as Code
**Project status:** Working CI prototype
**Repository:** https://github.com/Heytals/healthcare-devsecops-starter

## 1. Abstract

Healthcare Cloud Security Guardian is a prototype that demonstrates how infrastructure security checks can be integrated into a continuous integration (CI) workflow. It uses Terraform to represent cloud infrastructure, Checkov to scan infrastructure configuration, GitHub Actions to automate security checks, and Python scripts to generate findings and remediation proposals.

The project includes secure and intentionally insecure infrastructure examples, automated reporting, a local human-review workflow, and unit tests for review decisions. Remediation proposals are prepared for review rather than automatically applied. The current pipeline does not deploy cloud resources.

The objective is to demonstrate how selected infrastructure risks can be identified earlier in the development process and how security review can become a repeatable part of software delivery. This is an educational prototype, not a certified healthcare-compliance solution.

## 2. Introduction and Problem Statement

Healthcare environments may process sensitive information that requires careful protection. Misconfigured cloud storage or insufficient security controls can expose information, weaken confidentiality, and create operational or compliance risks.

Manual infrastructure reviews can be inconsistent and may occur too late in the development process. Infrastructure as Code (IaC) makes infrastructure configuration reviewable, while automated scanning can identify selected issues before deployment.

This project explores a preventive workflow in which infrastructure configuration is scanned during CI, findings are generated as machine-readable reports, and potential remediation actions are presented for human review.

## 3. Objectives

The primary objectives are to:

1. Represent cloud storage infrastructure using Terraform.
2. Scan infrastructure configuration using Checkov.
3. Run selected mandatory security checks through GitHub Actions.
4. Demonstrate detection of an intentionally insecure configuration.
5. Generate machine-readable security findings and remediation proposals.
6. Record approval and rejection decisions in a local review workflow.
7. Test review behavior using automated Python unit tests.
8. Demonstrate the workflow without requiring a live cloud deployment.
9. Document limitations and identify future improvements for industry use.

## 4. Scope

### Included in the current prototype

- Terraform examples representing secure and intentionally insecure configurations.
- Checkov-based infrastructure security scanning.
- GitHub Actions CI automation.
- A negative test that expects the insecure example to be rejected.
- JSON security findings and remediation proposals.
- Local proposal approval and rejection recording.
- Duplicate-review and unknown-proposal handling.
- Four automated unit tests for the review workflow.

### Outside the current scope

- Live AWS deployment or cloud account monitoring.
- Automatic execution of remediation changes.
- Authenticated multi-user review and enterprise role-based access control.
- Tamper-proof centralized audit storage.
- Certification or independent verification of regulatory compliance.

## 5. Technology Stack

| Technology | Role |
|---|---|
| Terraform | Describes representative cloud infrastructure |
| Checkov 3.3.29 | Scans Terraform configuration against selected security controls |
| Python 3.11 | Implements reporting, proposal generation, review logic, and tests |
| GitHub Actions | Automates security checks, reporting, and unit tests |
| Git and GitHub | Source control and CI workflow hosting |
| JSON / JSON Lines | Stores findings, proposals, and local review records |
| Visual Studio Code | Development environment |

## 6. System Architecture

The prototype follows this workflow:

```text
Developer commits code
        |
        v
GitHub repository
        |
        v
GitHub Actions
        |
        +---- Mandatory Checkov security gate
        |
        +---- Negative test for insecure configuration
        |
        +---- Guardian report generation
        |           |
        |           +---- security-findings.json
        |           |
        |           +---- remediation-proposals.json
        |
        +---- Python unit tests

Local reviewer
        |
        v
guardian/review.py
        |
        +---- review-audit.jsonl
        |
        +---- review-state.json
        |
        v
Decision recorded; infrastructure unchanged
```

The architecture separates detection, proposal generation, and review. The current review tool records a decision but does not apply a fix or modify cloud infrastructure.

**Figure 1:** System architecture. A polished diagram can be inserted here for the final submission.

## 7. Implementation

### 7.1 Infrastructure examples

The repository contains a secure Terraform example and an intentionally insecure example. They provide contrasting configurations for demonstrating infrastructure security scanning.

The secure example includes storage protection controls such as public-access restrictions, encryption, versioning, and policy rules. The intentionally insecure example is used to demonstrate the detection of selected misconfigurations.

These are demonstration configurations; their existence does not establish that a deployed environment would be secure.

### 7.2 Security scanning

Checkov evaluates Terraform configuration against selected controls. The CI workflow uses a defined list of checks for the mandatory security gate.

The pipeline also runs a negative test against the intentionally insecure example. The negative test expects Checkov to report failed checks, rather than treating every non-zero command result as proof of successful detection.

### 7.3 Automated reporting

The Guardian scanner generates `reports/security-findings.json`. The proposal-generation script produces `reports/remediation-proposals.json`.

Each proposal has an identifier, a source finding, and a review status. The current workflow uses the `pending_review` status for proposals awaiting a decision.

The CI reporting job uploads generated JSON files as a GitHub Actions artifact for inspection.

### 7.4 Human-reviewed proposals

The local review script, `guardian/review.py`, accepts a proposal ID, a decision, a reviewer-supplied identifier, and an optional note.

Supported decisions are `approve` and `reject`. The script records review events and maintains a review-state snapshot. It blocks unknown proposal IDs and duplicate decisions.

Approval does not mean a fix was executed. The current implementation records decisions locally and explicitly leaves infrastructure unchanged.

### 7.5 Continuous integration

The workflow is defined in `.github/workflows/security.yml`. It runs on pushes to `main` and on pull requests.

The latest verified workflow run, for commit `e6921b6`, completed successfully in approximately 1 minute and 2 seconds. The workflow contained four successful jobs:

1. Mandatory S3 privacy controls.
2. Negative test for the intentionally insecure example.
3. Guardian report generation.
4. Guardian unit tests.

The successful run demonstrates that the configured checks and tests passed for that revision. It does not prove that every possible security issue is detected.

## 8. Testing and Results

### 8.1 Automated unit tests

The local command used was:

```bat
python -m unittest discover -s tests -v
```

The four tests passed:

| Test | Expected behavior | Observed result |
|---|---|---|
| Approval | Records approved status without executing a fix | Passed |
| Rejection | Records rejected status | Passed |
| Duplicate review | Blocks a second decision for the same proposal | Passed |
| Unknown proposal | Rejects a proposal ID that does not exist | Passed |

**Local test result:** 4 tests ran; all 4 passed.

### 8.2 Continuous integration result

The GitHub Actions run associated with commit `e6921b6` completed with a successful status. All four workflow jobs displayed successful results.

**Evidence to insert:** Screenshot of the completed GitHub Actions run, including the four job results.

### 8.3 Security scan findings

The local Checkov report for the secure Terraform example recorded:

| Result category | Count |
|---|---:|
| Passed | 31 |
| Failed | 7 |
| Skipped | 2 |
| Parsing errors | 0 |
| Resources counted | 14 |

These counts reflect the earlier local scan recorded in `reports/security-findings.json`. They are not the same as the result of the CI mandatory security gate, which uses a selected subset of checks.

The seven reported failures included recommendations relating to S3 event notifications, cross-region replication, lifecycle configuration, and KMS key policy definition. These findings should be reviewed according to the intended threat model and deployment requirements; they should not be silently described as passed.

**Evidence to insert:** Screenshot or sanitized extract of the JSON summary and relevant Checkov findings.

### 8.4 Interpretation

The results demonstrate that the prototype can execute configured security checks, generate machine-readable findings, prepare proposals for review, and test the review workflow.

A successful CI run means that the workflow's configured requirements were satisfied. It does not establish complete security, production readiness, or regulatory compliance.

## 9. Security, Privacy, and Compliance Considerations

Healthcare infrastructure can involve sensitive data, so any production implementation would require substantially more controls than this prototype provides.

- No real patient data should be used in this demonstration.
- No cloud resources are deployed by the current workflow.
- The review tool uses a reviewer-supplied name and does not authenticate the reviewer's identity.
- Local audit files are not tamper-proof enterprise audit records.
- The current prototype does not execute approved remediation changes.
- Checkov only evaluates the controls that are configured and applicable to the scanned files.
- Passing the selected checks is not proof of HIPAA compliance or compliance with any other regulation.

A production implementation would require threat modeling, least-privilege identity controls, protected audit storage, centralized logging, monitoring, change-management controls, and qualified security and compliance review.

## 10. Limitations

The main limitations of the current version are:

1. **No live monitoring:** It scans repository configuration in CI rather than monitoring a connected cloud account.
2. **No automatic remediation:** It creates proposals but does not generate and apply production fixes end to end.
3. **Local review state:** Review records are stored locally and lack enterprise identity and concurrency protections.
4. **Limited policy coverage:** The pipeline enforces a selected set of security checks rather than every possible control.
5. **No compliance certification:** The project demonstrates technical controls but does not establish legal or regulatory compliance.

## 11. Future Enhancements

Potential improvements include:

- A dashboard for findings, risk prioritization, and review status.
- Authenticated reviewers and role-based access control.
- Safer, concurrency-aware review decisions and tamper-evident audit storage.
- Expanded policy coverage and automated regression testing.
- Generation of proposed configuration patches for staff approval.
- A separate, least-privilege remediation execution stage with explicit authorization.
- Optional cloud integration, monitoring, and alerting with strict cost controls.
- Mapping security evidence to applicable organizational controls, reviewed by qualified professionals.

These are future enhancements, not features claimed as complete in the current prototype.

## 12. Conclusion

Healthcare Cloud Security Guardian demonstrates a preventive DevSecOps workflow for representative cloud infrastructure. It combines Terraform, Checkov, GitHub Actions, Python reporting, review proposals, and automated tests to make selected infrastructure risks visible earlier in development.

The verified CI run and four passing unit tests provide evidence that the configured pipeline and review behaviors operate as intended. The project remains a prototype: it does not deploy infrastructure, execute remediation, or certify regulatory compliance.

The next stage is to improve reviewer identity, audit integrity, policy coverage, usability, and safe integration with cloud environments before considering production use.
