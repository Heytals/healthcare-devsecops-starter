# Project Report: Healthcare Cloud Security with DevSecOps

## 1. Abstract
This project demonstrates a preventive security workflow for cloud infrastructure. Terraform
describes the desired resources, Checkov scans the configuration, and GitHub Actions automates
the scan on code changes. The demonstration compares an intentionally insecure storage example
with a hardened example. It is an educational prototype, not a legal compliance certification.

## 2. Problem Statement
Healthcare organizations handle sensitive patient information. An incorrectly configured cloud
storage resource may expose data or fail required security controls. Manual review alone can be
inconsistent and slow.

## 3. Objectives
- Describe cloud resources as code.
- Detect selected misconfigurations before deployment.
- Run security checks automatically on repository changes.
- Demonstrate how a failed check can stop the CI pipeline.
- Document the prototype's limitations.

## 4. Technology Stack
- Terraform: Infrastructure as Code
- Checkov: Infrastructure security scanning
- GitHub: Source control and collaboration
- GitHub Actions: Continuous Integration workflow

## 5. Architecture
Developer commit -> GitHub Actions -> Checkov -> pass/fail result.
The prototype scans configuration and does not deploy resources.

## 6. Implementation
Describe the secure and intentionally insecure Terraform examples, installation, scan commands,
and the GitHub Actions workflow. Insert your own screenshots.

## 7. Test Cases
1. Scan the insecure example; record the findings and exit status.
2. Scan the secure example; record findings and any remaining warnings.
3. Push a change to GitHub and verify the Actions workflow runs.
4. In a test branch, introduce a controlled insecure setting, verify the pipeline response, and
   revert it afterward. Never apply the insecure configuration.

## 8. Results
Insert actual results and screenshots. Do not claim a test passed unless you ran it.
Record tool versions and any findings.

## 9. Limitations and Future Work
This prototype is not proof of HIPAA or other legal compliance. Future work may add custom policy
checks, secret scanning, dependency scanning, cloud configuration monitoring, approval gates,
and an isolated cloud test deployment.

## 10. Conclusion
Automating infrastructure checks can detect selected misconfigurations earlier and make security
part of the development workflow. Passing a scan does not guarantee complete security.
