# Healthcare Cloud Security DevSecOps (Beginner Starter)

## Goal
Demonstrate how Infrastructure as Code (Terraform), static security scanning (Checkov),
CI/CD (GitHub Actions), and compliance rules work together to reduce cloud misconfiguration risk.

**Safety:** This starter is a lab/demo, not a certified healthcare-compliance solution.
It does not deploy anything by default. Do not use real patient data. Review costs and security
before deploying to any cloud account.

## Architecture
Developer commit -> GitHub Actions -> Checkov scans Terraform -> workflow passes or fails.
The secure example is scanned in CI. The intentionally insecure example is used only for a
local negative test to demonstrate detection.

## Prerequisites
- Git and a GitHub account
- Python 3.10+ (for Checkov)
- Terraform CLI (optional for validation; no cloud credentials needed for scanning)
- VS Code or another text editor

## Step 1 — Install Checkov
Create/activate a virtual environment if you like, then run:
```bash
python -m pip install --upgrade pip
python -m pip install checkov
checkov --version
```

## Step 2 — Test the examples locally
From the repository root:
```bash
checkov -d examples/secure --framework terraform
```
Review findings and fix any applicable findings before treating a pass as meaningful.
Then scan the intentionally insecure example:
```bash
checkov -d examples/insecure --framework terraform
```
The insecure example is expected to produce findings and a non-zero exit code. Some Checkov
versions/rules may differ, so inspect the report rather than relying only on the exit code.

Optional Terraform syntax validation (does not create resources):
```bash
terraform -chdir=examples/secure init -backend=false
terraform -chdir=examples/secure validate
```
If `terraform init` downloads providers, it needs internet access. No `terraform apply` is required.

## Step 3 — Put it on GitHub
1. Create a new empty GitHub repository.
2. Unzip/copy these files into it.
3. In a terminal in the project folder:
```bash
git init
git add .
git commit -m "Add healthcare DevSecOps starter"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the URL with your own repository URL. Never commit cloud credentials or secrets.

## Step 4 — See CI/CD work
The workflow at `.github/workflows/security.yml` scans only the secure example on pushes and pull
requests. Open the repository's **Actions** tab to see the result. To demonstrate a blocked change,
temporarily introduce a clearly insecure setting into `examples/secure/main.tf`, push to a test
branch, and observe whether the scanner fails. Revert the change after the demonstration.
Do not make a real public cloud resource.

## Step 5 — Your demonstration
1. Explain the healthcare risk: a misconfigured storage resource can expose sensitive records.
2. Show `examples/insecure/main.tf` and run Checkov against it.
3. Show `examples/secure/main.tf` and run Checkov against it.
4. Show the GitHub Actions workflow and a run in the Actions tab.
5. Explain that a failed scan should block the pipeline; a passing scan means only that the
   configured checks passed, not that the system is perfectly secure or legally compliant.

## Project scope and limitations
- Uses an S3 bucket as a representative storage resource, not a real patient database.
- Does not prove HIPAA or any other regulation compliance by itself.
- Production systems need threat modeling, identity/access controls, logging, monitoring,
  encryption/key management, change approval, policy review, and periodic audits.
- The workflow scans code; it does not deploy infrastructure.
