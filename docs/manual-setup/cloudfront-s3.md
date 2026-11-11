# Static site hosting: S3 + CloudFront

## Architecture
Browser, CloudFront (HTTPS, cache), private S3 bucket.
The bucket is not public. Only this CloudFront distribution can read it.

## S3 bucket
| Setting | Value | Why |
|---|---|---|
| Name | `<prefix>-<account-id>-ap-south-1-an` | Account regional namespace: the name is reserved to this account and cannot be claimed by others after deletion |
| Region | ap-south-1 | |
| Block Public Access | all on | Bucket stays private |
| Static website hosting | off | Not needed. CloudFront reads the bucket through its S3 API |
| Contents | files from `frontend/` at the bucket root | `index.html`, `css/`, `js/` |

## CloudFront distribution
| Setting | Value | Why |
|---|---|---|
| Origin | the S3 bucket (S3 origin, not website endpoint) | |
| Origin access | Origin access control (OAC), signing on | CloudFront signs requests so a private bucket can serve it |
| Default behavior (`*`) | the S3 origin | The only behavior needed |
| Viewer protocol policy | Redirect HTTP to HTTPS | No insecure pages |
| Default root object | `index.html` | Serves the page for `/` |
| Pricing plan | Free flat-rate plan | $0, no overage charges |

## Bucket policy
Allows only this distribution to read objects:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontServicePrincipalReadOnly",
    "Effect": "Allow",
    "Principal": { "Service": "cloudfront.amazonaws.com" },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::<BUCKET_NAME>/*",
    "Condition": {
      "StringEquals": {
        "AWS:SourceArn": "arn:aws:cloudfront::<ACCOUNT_ID>:distribution/<DISTRIBUTION_ID>"
      }
    }
  }]
}
```

## Publishing a change (manual, for now)
1. S3, upload changed files, keeping paths (`index.html`, `css/`, `js/`).
2. Set metadata `Cache-Control: max-age=60` on each file.
3. CloudFront, Invalidations, create `/*`. Wait for Completed.
4. Check the page in a private window.

## Verify
- `https://<DISTRIBUTION_DOMAIN>.cloudfront.net/` loads over HTTPS.
- Opening the bucket's own S3 address returns 403 (it is private).

## Lessons learned
- Delete references before the thing they point to. I deleted the old
  bucket first, which left the distribution pointing at a missing origin.
- A distribution must always keep at least one origin. Add the new origin
  first, switch the behavior, then remove the old one.
- To delete a distribution on a flat-rate plan, cancel the plan first.
- CloudFront caches files (24 hours by default). Uploading to S3 alone does
  not update what visitors see, so invalidate or use short Cache-Control.
- Private S3 buckets report a missing file as 403, not 404.

## Status
Manual setup. Deployment to be automated with GitHub Actions.