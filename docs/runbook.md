# Runbook

What to do when something looks wrong. Start with the quick check, then find the symptom in the table. For anything that affected the live site or taught something new, write a [postmortem](postmortems/TEMPLATE.md) afterwards.

## Quick health check

1. Open the live site in a private window: https://dxvjp1p2avy3e.cloudfront.net
2. Confirm the page loads over HTTPS and the visitor number appears and goes up on refresh.
3. If not, call the API directly (PowerShell, note `curl.exe`):
   ```
   curl.exe -X POST <ApiUrl from the stack Outputs>
   ```
   It must return `{"visits": <number>}`.

Where to find values:
- **`ApiUrl`, `TableName`, `FunctionName`:** CloudFormation, stack `cloud-resume-backend`, Outputs tab (region `ap-south-2`).
- **Lambda logs:** Lambda console, the function whose name starts with `cloud-resume-backend-`, Monitor, View CloudWatch logs.

## Symptoms

| Symptom | Likely cause | What to do |
|---|---|---|
| Page loads, counter shows `unavailable` | The call to the API failed | Press F12, open Console and Network, and read the message. See the next rows |
| Console says blocked by CORS policy | The API's allowed origin does not match the page's origin | Check the `SiteOrigin` parameter: `https://`, exact domain, no trailing slash, no path. Fix it and run `sam deploy` |
| Counter call returns 500 | Lambda error | Read the latest log lines. `AccessDenied` means the role's policy or table name is wrong. `KeyError: 'TABLE_NAME'` means the environment variable is missing |
| Counter call returns 404 | Wrong URL or method | The route is `POST /visits`. Check `API_URL` in `frontend/js/counter.js` ends with `/visits` |
| Counter call returns 429 | Throttle reached (2 requests per second) | Wait a second. If it is constant, someone is hammering the API: check the Billing page and the API metrics |
| `net::ERR_NAME_NOT_RESOLVED` | `counter.js` still has a placeholder or an old, deleted API address | Put the current `ApiUrl` in `counter.js`, upload, invalidate |
| Page is blank or `AccessDenied` XML | CloudFront cannot read the bucket, or `index.html` is missing | Check the bucket holds `index.html` at its root, the default root object is `index.html`, and the bucket policy names this distribution's ARN |
| `403` on `/favicon.ico` only | No favicon file exists | Harmless. Add a favicon or a `<link rel="icon">` to silence it |
| Old content still showing after an upload | CloudFront cached the previous file | Create an invalidation for `/*` and check in a private window |
| AWS CLI says endpoint cannot be reached | Wrong region code | Use `ap-south-2`. Run `aws configure set region ap-south-2` |
| AWS CLI says token expired or not logged in | Short-lived login expired | Run `aws login` |
| Budget or anomaly alert e-mail | Unexpected spend | Check Billing, Bills (by service) and Cost Explorer (by service, then region). Look for anything you do not recognise. Check the API request count |

## Rolling back

**Backend:**
1. `git log` to find the last good commit, then `git revert <bad-commit>`.
2. From `backend/`: `sam build`, then `sam deploy`. Read the change set.
3. Run the quick health check.

**Frontend:**
1. Restore the previous version of the file from Git.
2. Upload it to the bucket (keep the path), then invalidate `/*`.

## Reset or set the counter

1. Get `TableName` from the stack Outputs.
2. DynamoDB, that table, Explore table items, open the item `resume-site`, edit `visits`, save.

## Credentials and access

- CLI access uses `aws login` (temporary credentials). There are no access keys to rotate or leak.
- If the account looks compromised: sign in as root (it has MFA), check IAM for users or keys you did not create, check Billing, and review CloudTrail event history.

## After an incident

1. Write a postmortem from [the template](postmortems/TEMPLATE.md). Blameless: ask what in the process allowed it.
2. Turn the lessons into small action items, such as a new test, an alarm or a runbook line.
3. Update this runbook if a symptom was missing from the table.