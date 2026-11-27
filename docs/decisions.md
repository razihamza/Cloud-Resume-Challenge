# Decisions

A record of the choices I made on this project, why, and what each one costs me. Open items first, then decisions grouped by area.

## Open decisions

| Topic | Options | Current thinking |
|---|---|---|
| Terraform | Rebuild the same backend in Terraform as a second implementation | Planned after CI/CD. Terraform is named in many cloud and DevOps job postings, so it is worth knowing alongside SAM |
| Frontend hosting as code | Add S3 and CloudFront to the SAM template, or define them in Terraform | Undecided. They are set up by hand today |
| CI/CD authentication | GitHub OIDC role scoped to this project | Planned, no stored access keys |
| Custom domain | Route 53 plus an ACM certificate | Skipped for now, see decision 5 |

## Hosting

### 1. Private S3 bucket behind CloudFront with origin access control
- **Why:** the bucket is never public. CloudFront is the only reader, so visitors get HTTPS, caching and a single front door.
- **Alternative:** S3 static website hosting with a public bucket. Simpler, but no HTTPS on its own and anyone can read the bucket directly.
- **Trade-off:** more setup (OAC and a bucket policy), and a missing file shows up as 403, not 404.

### 2. Account regional namespace for the bucket name
- **Why:** the name is reserved to my account. With a global name, a deleted bucket's name can be claimed by anyone, which can be abused if anything still points at it.
- **Trade-off:** the account ID and region are part of the name, and the setting cannot be applied to an existing bucket.

### 3. Re-pointed the existing CloudFront distribution to the new bucket
- **Why:** it kept the same address and the Free flat-rate plan.
- **Context:** I deleted the old bucket before the distribution, which left it with a dangling origin. See the [postmortem](postmortems/2026-11-cloudfront-origin-deleted-bucket.md).
- **Alternative:** delete and recreate the distribution. Cleaner, but requires cancelling the pricing plan first.

### 4. CloudFront Free flat-rate plan
- **Why:** $0, with no overage charges, so a traffic flood cannot create a surprise bill.
- **Alternative:** pay-as-you-go. The permanent free allowance would also cover this site, but nothing caps unwanted traffic.
- **Trade-off:** the plan covers one distribution, cannot be moved to another, and must be cancelled before the distribution can be deleted.

### 5. No custom domain (for now)
- **Why:** it adds a recurring cost (a domain name each year plus a Route 53 hosted zone each month) and does not teach anything the rest of the project does not.
- **If I add one later:** request the ACM certificate in `us-east-1` (CloudFront only reads certificates there), add a DNS alias, and add the new origin to the API CORS setting (the `SiteOrigin` parameter in `template.yaml`).

### 6. Short cache lifetime plus invalidation
- **Why:** CloudFront keeps files for 24 hours by default, so uploads to S3 did not show up. Files get `Cache-Control: max-age=60`, and I invalidate `/*` after a deploy.
- **Trade-off:** slightly more requests reach S3. At this traffic the cost is negligible.

## Backend

### 7. API Gateway HTTP API instead of REST API
- **Why:** roughly a third of the price per request and simpler to configure. I do not need the extra REST features (API keys, request validation, caching).

### 8. `POST /visits` for the increment
- **Why:** the call changes data, so POST is the correct verb. Crawlers and prefetching can trigger GET requests, which would inflate the count.

### 9. DynamoDB on-demand with an AWS-owned encryption key
- **Why:** nothing to size at this traffic, and the AWS-owned key is free. A customer-managed KMS key would cost about $1 a month for no benefit here.

### 10. Atomic counter with `UpdateItem ADD`
- **Why:** the increment happens inside DynamoDB in one step, so simultaneous visitors cannot overwrite each other. Reading, adding in code and writing back could lose updates.

### 11. Single-purpose Lambda, configuration in an environment variable
- **Why:** one small function is easy to test and reason about. The table name comes from `TABLE_NAME`, so the code does not change between environments. The runtime version is set once, in `template.yaml`.

### 12. Throttling on the public API (2 requests per second, burst 5)
- **Why:** the endpoint is public and unauthenticated. The limit caps the worst-case bill if someone floods it. A personal site never needs that rate.

### 13. CORS limited to the site's exact origin
- **Why:** browsers only let the site read the API's responses. It is not a security boundary against other clients, which is why throttling exists too.

### 14. Infrastructure as code with AWS SAM
- **Why:** SAM is built for the Lambda, API and DynamoDB pattern, is short, and compiles to CloudFormation, which AWS stores state for. There is no state file to manage.
- **Alternatives:** CloudFormation directly (more verbose), Terraform (cloud-agnostic and widely requested, but needs a state backend). Terraform comes next as a second implementation.
- **Trade-off:** SAM and CloudFormation only work on AWS.
- **How I switched:** deployed the SAM stack next to the hand-built backend, tested it, pointed the site at it, carried over the count, then deleted the hand-built resources.

### 15. `DeletionPolicy: Retain` on the DynamoDB table
- **Why:** stateful resources should survive a stack deletion or replacement, so data is not lost by accident.
- **Trade-off:** tearing down needs one extra manual step. See [infrastructure.md](infrastructure.md).

### 16. Let CloudFormation name the resources, and manage the log group in the template
- **Why:** fixed names make replacing a resource fail. Generated names avoid that. A log group defined in the template gets a 30-day retention instead of keeping logs forever.

## Account and region

### 17. IAM user with MFA instead of IAM Identity Center
- **Why:** for one personal account it is simpler. Identity Center works through AWS Organizations, and accounts in an organization are not eligible for Free Tier plan benefits, so I avoided it.
- **Revisit:** with more than one account.

### 18. No access keys anywhere
- **Why:** long-lived keys are the most common way credentials leak. The CLI uses `aws login`, which gives short-lived credentials that refresh automatically. The pipeline will use OIDC.

### 19. One region: ap-south-2 (Hyderabad)
- **Why:** everything regional stays in one place, which keeps permissions, logs and billing easy to find. CloudFront is global, so visitors' speed does not depend on this choice.
- **Exception:** if a custom domain is added, the CloudFront certificate must be in `us-east-1`.

## Lessons learned

- Remove what points at a thing before deleting the thing.
- A CloudFront distribution must always keep at least one origin.
- Check the active plan and Free Tier page early. Allowances change.
- A missing file in a private bucket answers 403, so a 403 is not always a permissions problem.
- A region code needs its hyphens: `ap-south-2`, not `ap-south2`. A wrong region produces confusing endpoint errors.