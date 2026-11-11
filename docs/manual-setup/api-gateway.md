# API Gateway: visitor-counter-api (HTTP API)

## Purpose
Public HTTPS front door for the counter. Browsers call it from the site,
and it invokes the Lambda function.

## Configuration
| Setting | Value | Why |
|---|---|---|
| API type | HTTP API | About a third of the price of a REST API, simpler setup |
| Region | ap-south-1 | Same as Lambda and DynamoDB |
| Route | `POST /visits` | POST because the call changes data |
| Integration | Lambda: visitor-counter-function | Proxy integration |
| Stage | `$default`, auto-deploy on | One stage, changes go live automatically |
| Authorization | none | Public counter. Abuse is limited by throttling |

## CORS
| Setting | Value |
|---|---|
| Allow origin | `https://<DISTRIBUTION_DOMAIN>.cloudfront.net` (exact, https, no trailing slash) |
| Allow methods | POST, OPTIONS |
| Allow headers | content-type |

Browsers block a page from reading another origin's responses unless that
origin allows it. If the site gets a custom domain, add it here.

## Throttling (cost guard)
Stage `$default`: rate 2 requests/second, burst 5. This caps the worst-case
bill if someone hammers the public endpoint.

## Endpoint
`https://<API_ID>.execute-api.ap-south-1.amazonaws.com/visits`
(public by design, referenced in `frontend/js/counter.js`)

## Create it (console)
1. API Gateway, Create API, HTTP API, Build.
2. Add integration: Lambda, choose the function. Name the API.
3. Route: POST `/visits`. Keep stage `$default` with auto-deploy.
4. Configure CORS and stage throttling as above.

## Verify
```
curl.exe -X POST https://<API_ID>.execute-api.ap-south-1.amazonaws.com/visits
```
Expect `{"visits": <number>}`. The live page should show the same count.

## Troubleshooting
| Symptom | Cause |
|---|---|
| CORS error in browser console | Allowed origin does not match the page's origin exactly |
| 404 | Route method or path does not match `POST /visits` |
| 500 | Lambda error. Read its CloudWatch logs |
| 429 | Throttle reached |

## Status
Manual setup. To be replaced by `template.yaml` (SAM).