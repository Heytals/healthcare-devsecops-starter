# Presentation Outline (8–10 slides)

## Slide 1 — Title
Healthcare Cloud Security Using DevSecOps
Subtitle: Infrastructure as Code, Automated Scanning, CI/CD, and Compliance Checks

Speaker note: Introduce the goal: detect unsafe infrastructure settings before deployment.

## Slide 2 — Problem
- Healthcare data is sensitive.
- Misconfiguration can expose storage or weaken protection.
- Manual review can miss mistakes.

Speaker note: Use a fictional hospital and no real patient data.

## Slide 3 — Objectives
- Define infrastructure using code.
- Scan configurations automatically.
- Fail the pipeline when required checks fail.
- Show secure vs insecure examples.

## Slide 4 — Core Concepts
- Declarative Infrastructure: describe the desired state.
- Static Analysis: inspect configuration without deploying it.
- CI/CD: automate checks on code changes.
- Automated Compliance: enforce defined policies.

## Slide 5 — Technology Stack
Terraform, Checkov, GitHub, GitHub Actions.

Speaker note: Explain one sentence for each tool.

## Slide 6 — Architecture
Developer commit -> GitHub Actions -> Checkov -> pass/fail.
The demo scans code; it does not deploy to AWS.

## Slide 7 — Implementation
Show the Terraform secure example and the CI workflow.

## Slide 8 — Live Demo
1. Scan the intentionally insecure example.
2. Show the findings.
3. Scan the secure example and discuss results.
4. Show the GitHub Actions run.

## Slide 9 — Results and Limitations
Show real screenshots and observed output.
Explain that a passing scan does not prove full security or legal compliance.

## Slide 10 — Conclusion
Security checks can be automated early in the infrastructure workflow.
Future work: custom policies, monitoring, approval gates, and secret scanning.
