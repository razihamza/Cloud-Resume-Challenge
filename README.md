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
- [x] Testing for Lambda Function (Automated)
- [x] Infrastructure as code (SAM or CloudFormation) for the backend
- [ ] CI/CD with GitHub Actions
- [ ] Blog post about the build

## Structure

```
.
├── README.md
├── .gitignore
├── frontend/                  index.html, css/, js/counter.js
├── backend/
│   ├── template.yaml          the whole backend, as code
│   ├── samconfig.toml         deploy settings (stack name, region, tags)
│   ├── lambda/
│   │   └── lambda_function.py
│   ├── tests/                 pytest unit tests
│   ├── requirements-dev.txt
│   └── pytest.ini
└── docs/
    ├── decisions.md           why I chose what I chose
    ├── practices.md           how I work on this project
    ├── infrastructure.md      deploying, updating and tearing down
    ├── testing.md             how the tests work
    ├── runbook.md             what to do when something breaks
    ├── manual-setup/          hand-built setup records 
    └── postmortems/           blameless write-ups
```
## Documentation
- [CloudFront & S3 Setup](docs/manual-setup/cloudfront-s3.md)
- [DynamoDB](docs/manual-setup/dynamodb.md)
- [Lambda Function](docs/manual-setup/lambda.md)
- [API Gateway Setup](docs/manual-setup/api-gateway.md)
- [Infrastructure(SAM)]
- [Testing]
- [Runbook, When Something Breaks]

## Author

Mohammed Razi Hamza, IT Administrator moving into cloud infrastructure.
LinkedIn: https://www.linkedin.com/in/razihamza