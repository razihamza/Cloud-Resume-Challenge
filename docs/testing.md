# Testing

Unit tests for the Lambda function. They run the real function code against a fake, in-memory DynamoDB (using the `moto` library), so they are fast and can never touch the real table or the real counter.

## Run them

From `backend/` (PowerShell):

```
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

All tests should pass. Any test that fails prints what it expected and what it got.

## Layout

```
backend/
├── lambda/lambda_function.py     the code under test
├── tests/
│   ├── conftest.py               shared setup (fixtures)
│   └── test_lambda_function.py   the tests
├── requirements-dev.txt          pytest, moto, boto3
└── pytest.ini
```

## How the setup works

- **`aws_env`** (runs for every test): sets fake credentials, a region and a test table name, so even a mistake cannot log in to the real account.
- **`dynamodb_table`**: starts the fake AWS and creates an empty table shaped like the real one. Everything after the `yield` is cleanup, which destroys the fake AWS after each test.
- **`handler_module`**: imports the Lambda file only after the fake table exists, because the file reads `TABLE_NAME` and connects to DynamoDB the moment it is imported. Each test gets a fresh import.

## What each test protects

| Test | Catches |
|---|---|
| First call returns 1 and creates the item | Breaking the automatic item creation |
| Three calls return 1, 2, 3 | A wrong increment |
| Starts from an existing 41 and returns 42 | Overwriting the stored value instead of adding |
| Response is valid JSON with a whole number | Removing the `int()` conversion (DynamoDB returns a `Decimal`, which `json.dumps` cannot handle) |
| Table missing returns 500 with only a generic message | Leaking AWS error details to visitors |

## What they do not cover

These run against a fake AWS, so they cannot check:

- IAM permissions (the role's one-action policy)
- API Gateway routing, CORS and throttling
- CloudFront and S3 access

Those are checked after a deploy with a smoke test: a `POST` to the API URL must return a number, and the live page must show the counter. The CI pipeline will include this check.

## Adding a test

1. Write a function named `test_something_specific` in `tests/test_lambda_function.py`.
2. Ask for `handler_module` (and `dynamodb_table` if you need to read or write the table directly).
3. Call `handler_module.lambda_handler({}, None)` and `assert` what must be true.
4. Make it fail on purpose first, to prove it can catch the problem.

## Proving the tests work

Break the code on purpose and confirm the right tests fail, then undo with `git checkout backend/lambda/lambda_function.py`:

1. Change `":inc": 1` to `":inc": 2`. The counting tests should fail.
2. Remove the `int(...)` around the value. The JSON test should fail.
3. Replace the error body with `str(err)`. The 500 test should fail.

## Reading a failure

```
FAILED tests/test_lambda_function.py::test_counter_goes_up_by_one_on_every_call
E   assert [2, 4, 6] == [1, 2, 3]
```

On the `assert` line, the left side is what the code actually returned, and the right side is what the test expected.

## Planned

Run these tests automatically on every push with GitHub Actions, and block a merge or deploy if they fail.