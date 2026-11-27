# Engineering practices

How I work on this project, written down so the process is as reviewable as the code. Some of these are in place and some are planned. The status column says which.

## Practices at a glance

| Practice | Status | Where |
|---|---|---|
| Everything in version control | In place | This repository |
| Written decisions with reasons | In place | [decisions.md](decisions.md) |
| Backend as code, with a change-set preview before every deploy | In place | [infrastructure.md](infrastructure.md), `backend/template.yaml` |
| Setup documented so it can be rebuilt | In place | [manual-setup/](manual-setup/README.md) |
| Least privilege (IAM role, bucket policy) | In place | [account-security.md](manual-setup/account-security.md) |
| No access keys anywhere (`aws login`, short-lived credentials) | In place | [account-security.md](manual-setup/account-security.md) |
| Budget alerts and anomaly detection | In place | [account-security.md](manual-setup/account-security.md) |
| Blameless postmortems | In place | [postmortems/](postmortems/) |
| Runbook for common problems | In place | [runbook.md](runbook.md) |
| Unit tests for the Lambda function | Written | [testing.md](testing.md) |
| Tests run automatically on every push (CI) | Planned | GitHub Actions |
| Automated deployment with short-lived credentials | Planned | GitHub Actions with OIDC |
| Branches, pull requests, protected `main` | Planned | GitHub settings |
| Dependency updates and secret scanning | Planned | Dependabot, GitHub secret scanning |
| Alarm on Lambda errors | Planned | CloudWatch |
| S3 and CloudFront defined as code | Planned | SAM or Terraform |
| Resource tagging for cost tracking | In place for the backend | Stack tags in `samconfig.toml` |

## How a change flows

1. **Branch.** Make the change on a short-lived branch, not directly on `main`.
2. **Small commits** with clear messages that say what and why, for example `Return 500 without leaking AWS error text`.
3. **Test.** Add or update tests, and run them locally: `cd backend && python -m pytest -v`.
4. **Check the template** if infrastructure changed: `sam validate --lint`.
5. **Pull request.** Open a PR, read my own diff once, and check it for secrets and account IDs.
6. **Automatic checks.** CI will run the tests, and a failing test will block the merge.
7. **Merge, then deploy.** Backend: `sam build` and `sam deploy`, and read the change set before confirming. Frontend: upload and invalidate. Both will be automated later.
8. **Verify.** Run the smoke test (below).
9. **Record.** Update docs and the decision log if behavior or design changed.

## Definition of done for a change

- [ ] Change made on a branch and merged through a pull request
- [ ] Tests added or updated, and passing
- [ ] No secrets or account IDs in the diff (placeholders in documentation)
- [ ] Deployed
- [ ] Smoke test passed: a `POST` to the API URL returns a number, and the live page shows the counter
- [ ] CloudFront cache invalidated if frontend files changed
- [ ] Docs and [decisions.md](decisions.md) updated if something about the design changed
- [ ] Cost impact considered

## When something breaks

1. **Stop the damage first.** Roll back to the last good version (`git revert`, then `sam build` and `sam deploy`) before hunting for the cause.
2. **Look.** Follow the [runbook](runbook.md).
3. **Fix forward,** with a test that would have caught it.
4. **Write it up.** If the problem affected the live site or taught me something, write a postmortem from [the template](postmortems/TEMPLATE.md). Postmortems are blameless: they ask what in the process allowed the mistake, not who made it.

## Conventions

- **Placeholders, not identifiers,** in documentation: `<ACCOUNT_ID>`, `<API_ID>`, `<DISTRIBUTION_ID>`, `<BUCKET_NAME>`.
- **Delete what points at a thing before deleting the thing.** Learned the hard way, see the first postmortem. For the backend, let the stack do it (`sam delete`).
- **Source of truth is Git.** The S3 bucket and the AWS console are copies. Anything deployed should be rebuildable from this repository.
- **Never hand-edit what the template manages.** Change `template.yaml` and redeploy, or the console and the template drift apart.
- **One region:** `ap-south-2`, except CloudFront certificates (`us-east-1`) if a custom domain is added.