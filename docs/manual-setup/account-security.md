# AWS account security baseline

The security and cost baseline I set up before building anything in this personal AWS account. This file deliberately contains no account IDs, e-mail addresses or other identifiers.

## Principles

1. **Root is break-glass only.** It can do everything and IAM policies cannot restrict it, so it is protected heavily and almost never used.
2. **No long-lived credentials.** Leaked access keys are a common way accounts get compromised, so none are created.
3. **Least privilege.** Each identity gets only the actions it needs, on only the resources it needs.
4. **Billing is a security signal.** An unexpected bill is often the first sign of a compromised account, so alerts are on.

## Controls

### Root user
- Unique, long password.
- Multi-factor authentication with an authenticator app.
- No access keys. Verified (see below).
- Alternate contacts (billing, operations, security) filled in.
- Not used for daily work.

### Daily access
- An IAM user in an `admins` group, with MFA enabled.
- Console access only. No access keys.
- IAM access to billing information is activated at account level. Billing permissions are then controlled by IAM policy, not by the switch alone.

### Billing guardrails
- Zero-spend budget and a small monthly cost budget, both with e-mail alerts.
- Cost Anomaly Detection on.
- Free Tier usage alerts on.
- Free Tier page checked for what is still covered. The account is past its starter period, so only the always-free allowances apply and everything else is billed normally.

### Limiting the blast radius inside the project
| Area | Control |
|---|---|
| S3 | Bucket is private (Block Public Access on). Only the CloudFront distribution can read it, through origin access control and a bucket policy condition on the distribution ARN |
| Lambda | Execution role allows only `dynamodb:UpdateItem` on one table |
| DynamoDB | Encrypted with an AWS-owned key. No customer-managed KMS key to pay for or manage |
| API Gateway | Public by design, but throttled (2 requests per second, burst 5) and CORS-limited to the site's origin |

### Habits
- One working region (ap-south-1). If something seems missing, check the region selector first.
- Delete references before the thing they point to (DNS and CloudFront before buckets), to avoid dangling resources.
- No secrets in the repository. Placeholders are used for account and resource IDs in documentation.

## How to verify

| Check | Where |
|---|---|
| Root has MFA and no access keys | IAM, Credential report: the `<root_account>` row shows `mfa_active` true and both `access_key_*_active` false |
| Admin user has MFA and no keys | Same report, the user's row |
| Budgets exist and alert to a mailbox I read | Billing and Cost Management, Budgets |
| Nothing unexpected is running | Billing, Bills, expand by service. Cost Explorer grouped by service then region |

## Deliberate choices and limits

- **IAM user instead of IAM Identity Center.** For a single personal account this is simpler, and Identity Center requires AWS Organizations. See [decisions](../decisions.md). I would revisit this with more than one account.
- **Broad admin permissions for the daily user.** Acceptable for a one-person learning account. The deployment pipeline will not use them.
- **No hardware security key yet.** MFA uses an authenticator app. A passkey or hardware key as a second device would be stronger.

## Planned improvements

- GitHub Actions will deploy through an IAM role with OIDC, so no access keys are stored in GitHub. That role will be scoped to this project only.
- Review CloudTrail event history periodically.
- Add a second MFA device to root and the admin user.
