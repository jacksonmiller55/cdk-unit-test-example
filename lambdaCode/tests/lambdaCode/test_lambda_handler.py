import os
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

from lambdaCode.lambda_handler import (
    get_dynamo_db_table,
    validate_str_section,
    validate_guest,
    validate_phone_number,
    get_number_of_adults,
)
from lambdaCode.models.guest import Guest


@patch("lambdaCode.lambda_handler.boto3")
def test_dynamo_db_table_exception(mock_boto):
    with pytest.raises(Exception) as e_info:
        table = get_dynamo_db_table()
        assert (
            e_info.__str__() == "Unable to get 'TABLE_NAME' variable from environment"
        )


@patch("lambdaCode.lambda_handler.boto3")
def test_dynamo_db_table(mock_boto):
    with patch.dict(os.environ, {"TABLE_NAME": "TABLE_NAME"}, clear=True):
        res_table = get_dynamo_db_table()
        mock_boto.resource.assert_called_once_with("dynamodb")
        mock_boto.resource("dynamodb").Table.called_once_with("TABLE_NAME")
        exp = mock_boto.resource("dynamodb").Table("TABLE_NAME")
        assert exp == res_table


@patch("lambdaCode.lambda_handler.boto3")
def test_dynamo_db_table_bad(mock_boto):
    with patch.dict(os.environ, {"TABLE_NAME": "TABLE_NAME"}, clear=True):
        res_table = get_dynamo_db_table()
        exp = mock_boto.resource().Table()
        assert exp == res_table


@pytest.mark.parametrize(
    ("body", "section", "expected"),
    [
        ({"first_name": " John"}, "first_name", "John"),
        ({"last_name": "Smith "}, "last_name", "Smith"),
        (
            {"email_address": " John.Smith@email.com "},
            "email_address",
            "John.Smith@email.com",
        ),
        ({"last_name": "Smith"}, "last_names", None),
        ({"email_address": " John.Smith@email.com "}, "last_name", None),
    ],
)
def test_validate_str_section(expected, section, body):
    result = validate_str_section(body, section)
    assert result == expected


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            {
                "last_name": "Smith ",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": True,
            },
            "first_name: is required",
        ),
        (
            {
                "first_name": " ",
                "last_name": "Smith ",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": True,
            },
            "first_name: is required",
        ),
        (
            {
                "first_name": None,
                "last_name": "Smith ",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": True,
            },
            "first_name: is required",
        ),
        (
            {
                "first_name": " John",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": True,
            },
            "last_name: is required",
        ),
        (
            {
                "first_name": " John",
                "last_name": " ",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": True,
            },
            "last_name: is required",
        ),
        (
            {
                "first_name": " John",
                "last_name": None,
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": True,
            },
            "last_name: is required",
        ),
        (
            {
                "first_name": " John",
                "last_name": "Smith ",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
                "not_attending": 0,
            },
            "not_attending: is required and must be a bool",
        ),
        (
            {
                "first_name": " John",
                "last_name": "Smith ",
                "email_address": " John.Smith@email.com ",
                "phone_number": "1234",
                "total_number_of_guests_attending": "0",
            },
            "not_attending: is required and must be a bool",
        ),
    ],
)
def test_validate_guest_invalid(expected, body):
    with pytest.raises(ValueError) as e_info:
        result = validate_guest(body)
    assert expected == e_info.value.__str__()


@patch("lambdaCode.models.guest.datetime")
def test_validate_guest_valid(mock_datetime):
    exp_datetime = datetime(2022, 3, 30)
    mock_datetime.now.return_value = exp_datetime
    exp_first_name = "first"
    exp_last_name = "last"
    exp_phone_number = "2345678910"
    exp_email_address = "email@address.com"
    exp_total_number_of_guests_attending = 123
    exp_not_attending = True

    body = {
        "first_name": exp_first_name,
        "last_name": exp_last_name,
        "email_address": exp_email_address,
        "phone_number": "1" + exp_phone_number,
        "total_number_of_guests_attending": exp_total_number_of_guests_attending.__str__(),
        "not_attending": "True",
    }
    exp = Guest(
        exp_first_name,
        exp_last_name,
        exp_phone_number,
        exp_email_address,
        exp_total_number_of_guests_attending,
        exp_not_attending,
    )
    result = validate_guest(body)
    assert type(result) == type(exp)
    assert result.first_name == exp_first_name
    assert result.last_name == exp_last_name
    assert result.phone_number == exp_phone_number
    assert result.email_address == exp_email_address
    assert (
        result.total_number_of_guests_attending == exp_total_number_of_guests_attending
    )
    assert result.not_attending == exp_not_attending
    assert result.first_name_lower == exp_first_name.lower()
    assert result.last_name_lower == exp_last_name.lower()
    assert result.last_updated == exp_datetime


def test_validate_guest_valid_better():
    # TODO
    assert True is True


@pytest.mark.parametrize(
    ("body", "section", "expected"),
    [
        ({"phone_number": " 12345678910     "}, "phone_number", "2345678910"),
        ({"phone_number": " 2345678910     "}, "phone_number", "2345678910"),
        ({"phone_number": "      "}, "phone_number", None),
        ({}, "phone_number", None),
    ],
)
def test_validate_phone_number(expected, section, body):
    result = validate_phone_number(body, section)
    assert result == expected


@pytest.mark.parametrize(
    ("body", "section", "expected"),
    [
        (
            {"total_number_of_guests_attending": " 2 "},
            "total_number_of_guests_attending",
            2,
        ),
        (
            {"total_number_of_guests_attending": "  "},
            "total_number_of_guests_attending",
            0,
        ),
        ({}, "total_number_of_guests_attending", 0),
    ],
)
def test_get_number_of_adults(expected, section, body):
    result = get_number_of_adults(body, section)
    assert result == expected


def test_get_number_of_adults_failed():
    body = {"total_number_of_guests_attending": "a"}
    section = "total_number_of_guests_attending"
    expected = "total_number_of_guests_attending: must be an int"

    with pytest.raises(ValueError) as e_info:
        result = get_number_of_adults(body, section)
    assert e_info.value.__str__() == expected


def test_insert_update_guest():
    # TODO
    assert False == False
