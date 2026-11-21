import json

import pytest


def visits_from(result):
    """Pull the visit number out of a Lambda response."""
    return json.loads(result["body"])["visits"]


def test_first_call_creates_the_counter_and_returns_one(handler_module, dynamodb_table):
    result = handler_module.lambda_handler({}, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"visits": 1}

    # The item did not exist before. The function must have created it.
    item = dynamodb_table.get_item(Key={"id": "resume-site"})["Item"]
    assert item["visits"] == 1


def test_counter_goes_up_by_one_on_every_call(handler_module):
    numbers = [visits_from(handler_module.lambda_handler({}, None)) for _ in range(3)]

    assert numbers == [1, 2, 3]


def test_counter_continues_from_an_existing_value(handler_module, dynamodb_table):
    dynamodb_table.put_item(Item={"id": "resume-site", "visits": 41})

    result = handler_module.lambda_handler({}, None)

    assert visits_from(result) == 42


@pytest.mark.parametrize(
    "event",
    [
        {},
        {"requestContext": {"http": {"method": "POST", "path": "/visits"}}},
    ],
)
def test_response_is_valid_json_with_a_whole_number(handler_module, event):
    result = handler_module.lambda_handler(event, None)

    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "application/json"
    # json.dumps fails on DynamoDB's Decimal type, so this also proves the
    # int() conversion in the function is working.
    assert isinstance(visits_from(result), int)


def test_database_failure_returns_500_without_leaking_details(
    handler_module, dynamodb_table
):
    # Deleting the table makes the next DynamoDB call fail, like a real outage.
    dynamodb_table.delete()

    result = handler_module.lambda_handler({}, None)

    assert result["statusCode"] == 500
    # Exactly this and nothing more: no table name, no AWS error text.
    assert json.loads(result["body"]) == {"error": "internal error"}
