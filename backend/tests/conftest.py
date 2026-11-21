"""Shared test setup (fixtures).

Goal: run the real Lambda code against a FAKE DynamoDB that lives only in
memory, so the tests can never touch the real table or the real counter.
"""
import sys
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

# The Lambda folder is called "lambda", which is a reserved word in Python and
# cannot be imported as a package. Adding it to the import path lets the tests
# do a plain "import lambda_function".
LAMBDA_DIR = Path(__file__).resolve().parents[1] / "lambda"
sys.path.insert(0, str(LAMBDA_DIR))

TABLE_NAME = "visitor-counter-test"
REGION = "ap-south-1"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    """Fake credentials, region and table name for every test.

    The fake credentials mean that even if something escaped the mock, it
    could not log in to your real AWS account.
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION)
    monkeypatch.setenv("TABLE_NAME", TABLE_NAME)


@pytest.fixture
def dynamodb_table(aws_env):
    """Start the fake AWS and create an empty table, like the real one."""
    with mock_aws():
        resource = boto3.resource("dynamodb", region_name=REGION)
        table = resource.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


@pytest.fixture
def handler_module(dynamodb_table):
    """Import the Lambda code AFTER the fake table exists.

    lambda_function.py reads TABLE_NAME and creates its DynamoDB connection
    the moment it is imported. So the environment and the fake AWS must be
    ready first. Removing it from sys.modules forces a fresh import for every
    test, so one test cannot affect another.
    """
    sys.modules.pop("lambda_function", None)
    import lambda_function

    return lambda_function
