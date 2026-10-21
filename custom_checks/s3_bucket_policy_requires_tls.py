from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3BucketPolicyRequiresTLS(BaseResourceCheck):
    """Project-local guardrail: S3 bucket policies must deny non-TLS requests."""

    def __init__(self) -> None:
        name = "S3 bucket policy denies requests that do not use TLS"
        check_id = "CKV_AWS_999"
        supported_resources = ("aws_s3_bucket_policy",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=check_id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def _flatten(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(
                f"{self._flatten(key)} {self._flatten(item)}"
                for key, item in value.items()
            )
        if isinstance(value, (list, tuple)):
            return " ".join(self._flatten(item) for item in value)
        return str(value)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        policy_text = self._flatten(conf.get("policy", [])).lower()

        # This simple educational check looks for the key components of the
        # explicit deny statement in the Terraform policy expression.
        required_terms = ("aws:securetransport", "deny", "false")
        if all(term in policy_text for term in required_terms):
            return CheckResult.PASSED

        return CheckResult.FAILED


check = S3BucketPolicyRequiresTLS()
