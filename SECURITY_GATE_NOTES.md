# Security gate update: how to use it

## Files included

- `examples/secure/main.tf`: example controls for a private S3 data bucket, KMS encryption, versioning, access logging, and HTTPS-only requests.
- `.github/workflows/security.yml`: CI workflow that runs the mandatory checks on the secure example and includes a negative test to prove the insecure example is rejected.
- `custom_checks/s3_bucket_policy_requires_tls.py`: a small project-local Checkov rule that checks for the key elements of an S3 bucket-policy denial for non-TLS requests.

## Apply the update safely

1. In VS Code, make a backup of your current `examples/secure/main.tf` and `.github/workflows/security.yml`.
2. Copy the files from this patch into the matching paths in your project. Keep `examples/insecure/main.tf` unchanged because it is the deliberately vulnerable demo.
3. Do not run `terraform apply`. This is an educational configuration example and uses placeholder bucket names.
4. In the activated `.venv` terminal, run:

   ```bat
   checkov -d examples/secure --framework terraform --external-checks-dir custom_checks --check CKV_AWS_7,CKV_AWS_18,CKV_AWS_19,CKV_AWS_20,CKV_AWS_21,CKV_AWS_53,CKV_AWS_54,CKV_AWS_55,CKV_AWS_56,CKV_AWS_57,CKV_AWS_145,CKV2_AWS_6,CKV_AWS_999
   ```

5. Then test that the intentionally insecure sample is rejected:

   ```bat
   checkov -d examples/insecure --framework terraform --external-checks-dir custom_checks --check CKV_AWS_7,CKV_AWS_18,CKV_AWS_19,CKV_AWS_20,CKV_AWS_21,CKV_AWS_53,CKV_AWS_54,CKV_AWS_55,CKV_AWS_56,CKV_AWS_57,CKV_AWS_145,CKV2_AWS_6,CKV_AWS_999
   ```

   The insecure scan should report failures and return a non-zero exit code. That is the expected result for this negative test.

## Why the workflow scans two folders differently

- `examples/secure` is the configuration the main security gate must approve.
- `examples/insecure` is intentionally unsafe. The negative-test job succeeds only when Checkov proves that the unsafe sample fails the selected checks.

## Controls enforced by the gate

- S3 access logging on the data bucket
- Encryption at rest, including customer-managed KMS encryption for the data bucket
- Automatic rotation enabled for the customer-managed KMS key
- No public read/write ACLs
- Versioning
- All four S3 public-access-block settings
- A project-local check for a bucket policy denying requests that do not use TLS

The dedicated access-log destination has two inline, justified Checkov suppressions: it does not log to itself (to avoid recursive logs), and it uses SSE-S3 because AWS server-access-log destination buckets do not support SSE-KMS.

## Findings intentionally not in the mandatory gate

Checkov may still report recommendations such as lifecycle configuration, event notifications, or cross-region replication. These are not silently disabled with `--soft-fail`: they are outside this initial mandatory-check allow-list because they require explicit decisions about retention, monitoring/response, and data-residency/disaster-recovery requirements. Review and document them before claiming production readiness.

This project is a learning prototype, not a legal certification or proof of HIPAA compliance. Do not store real patient data or deploy this example into a production account.
