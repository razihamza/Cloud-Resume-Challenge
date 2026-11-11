# Cloud Resume Challenge

My implementation of the [Cloud Resume Challenge](https://cloudresumechallenge.dev/docs/the-challenge/): a resume website built and run entirely on AWS.

## Current status

- [x] Resume page in HTML and CSS
- [x] Hosted on S3
- [x] HTTPS via CloudFront
- [ ] Custom domain (Route 53) - optional
- [x] Visitor counter (JavaScript, API Gateway, Lambda, DynamoDB)
- [x] Testing for Lambda Function
- [ ] Infrastructure as code (SAM or CloudFormation)
- [ ] CI/CD with GitHub Actions

## Structure

```
index.html      resume page
css/style.css   styling
js/counter.js   visitor counter js
```