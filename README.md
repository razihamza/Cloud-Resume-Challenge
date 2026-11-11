# Cloud Resume Challenge

My implementation of the [Cloud Resume Challenge](https://cloudresumechallenge.dev/docs/the-challenge/): a resume website built and run entirely on AWS, with a serverless visitor counter.

**Live site:** https://dxvjp1p2avy3e.cloudfront.net

## Current status

- [x] Resume page in HTML and CSS
- [x] Hosted on S3
- [x] HTTPS via CloudFront
- [ ] Custom domain (Route 53) - optional
- [x] Visitor counter (JavaScript, API Gateway, Lambda, DynamoDB)
- [x] Account security baseline and cost alerts
- [ ] Testing for Lambda Function (Automated)
- [ ] Infrastructure as code (SAM or CloudFormation) for the backend
- [ ] CI/CD with GitHub Actions
- [ ] Blog post about the build

## Structure

```
frontend/index.html                 resume page
frontend/css/style.css              styling
frontend/js/counter.js              visitor counter js
backend/lambda/lambda_function.py   dynamodb update function
docs/manual-setup/dynamodb.md
docs/manual-setup/lambda.md
docs/manual-setup/api-gateway.md
docs/manual-setup/cloudfront-s3.md
```
## Documentation
- [CloudFront & S3 Setup](docs/manual-setup/cloudfront-s3.md)
- [DynamoDB](docs/manual-setup/dynamodb.md)
- [Lambda Function](docs/manual-setup/lambda.md)
- [API Gateway Setup](docs/manual-setup/api-gateway.md)

## Author

Mohammed Razi Hamza, IT Administrator moving into cloud infrastructure.
LinkedIn: https://www.linkedin.com/in/razihamza