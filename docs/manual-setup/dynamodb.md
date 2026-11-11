# DynamoDB table: visitor-counter

## Purpose
Stores the site's visit count as a single item. The Lambda function
increments it on every page load.

## Configuration
| Setting | Value | Why |
|---|---|---|
| Table name | visitor-counter | Read by Lambda through the TABLE_NAME variable |
| Region | ap-south-1 (Mumbai) | Same region as the S3 bucket and Lambda |
| Partition key | id (String) | One item per counter |
| Sort key | none | Not needed |
| Capacity mode | On-demand | Pay per request. Nothing to size at this traffic |
| Encryption | Owned by Amazon DynamoDB | Free. Avoids a customer-managed KMS key (about $1/month) |
| Point-in-time recovery | Off | Not needed for a counter |

## Data model
```json
{ "id": "resume-site", "visits": 42 }
```
The item is created automatically on the first increment.

## Access pattern
- One operation: `UpdateItem` with `ADD #v :inc`.
- The increment is atomic, so simultaneous visitors cannot overwrite each other.
- The Lambda role may only call `dynamodb:UpdateItem` on this table (least privilege).

## Create it (console)
1. DynamoDB, Create table.
2. Name `visitor-counter`, partition key `id` (String).
3. Customize settings, On-demand, encryption "Owned by Amazon DynamoDB".
4. Create table.

## Verify
Call the API once, then open Explore table items and check `visits` increased.

## Reset the counter
Explore table items, edit the item, set `visits` to the number you want.

## Cost
Fractions of a cent at personal-site traffic. Billed per request.

## Status
Manual setup. To be replaced by `template.yaml` (SAM).