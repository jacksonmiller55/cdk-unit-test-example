import logging
import os
import boto3
import json

from lambdaCode.models.response import Response
from lambdaCode.models.guest import Guest

logger = logging.getLogger("APP")
logger.setLevel(logging.INFO)


def handler(event: dict, context):
    """
    Main entry point for the lambda
    Args:
        event (dict): contains the lambda event info
        context: context of the lambda

    Returns:
        dict: lambda response

    """
    logger.info(f"[REQUEST]: {json.dumps(event)}")
    method = event["httpMethod"]
    route = event["pathParameters"]["proxy"]
    body = (
        json.loads(event["body"])
        if "body" in event and event["body"] is not None
        else {}
    )
    headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}

    try:
        if method.upper() == "POST" and route == "rsvp":
            guest = validate_guest(body)
            guest_status_code = insert_update_guest(guest)
            if guest_status_code != 200:
                raise ValueError("Failure to add guest: {}".format(guest_status_code))
            response = Response(
                status_code=200,
                headers=headers,
                body={"guest": json.loads(json.dumps(guest))},
            ).to_dict()
            logger.info(f"[RESPONSE]: {response}")
            return response
        else:
            response = Response(
                status_code=404, headers={}, body={"message": "{}"}
            ).to_dict()
            logger.info(f"[RESPONSE]: {response}")
            return response
    except Exception as e:
        logger.exception(e)
        response = Response(
            status_code=500, headers={}, body={"error": e.__str__()}
        ).to_dict()
        logger.info(f"[RESPONSE]: {response}")


def validate_str_section(body: dict, section: str) -> str or None:
    """
        validates a str section of the request
    Args:
        body (dict): contains the lambda event info
        section (str): section of the request to analyze
    Returns:
        str or None: validated section of the response
    """
    if section in body and body[section] is not None and body[section].strip() != "":
        value: str = body[section].strip()
    else:
        value: None = None
    return value


def validate_phone_number(body: dict, section: str) -> str or None:
    """
        Validates the phone number in the response
    Args:
        body (dict): contains the lambda event info
        section (str): section of the request to analyze
    Returns:
        str or None: Validated phone number
    """
    if (
        section in body
        and body[section] is not None
        and type(body[section]) == str
        and body[section].strip() != ""
    ):
        phone_number: str = "".join(filter(lambda x: x.isdigit(), body[section]))
        if phone_number.startswith("1"):
            phone_number: str = phone_number[1::]
        if len(phone_number) > 10 or len(phone_number) < 10:
            phone_number: None = None
    else:
        phone_number: None = None
    return phone_number


def get_number_of_adults(body: dict, section: str) -> int:
    """
        Validates the total number of kids that will be attending
    Args:
        body (dict): contains the lambda event info
        section (str): section of the request to analyze
    Returns:
        int: total number of kids attending
    """
    if (
        section in body
        and body[section] is not None
        and type(body[section]) == str
        and body[section].strip() != ""
    ):
        try:
            value = int("".join(filter(lambda x: x.isdigit(), body[section])))
        except:
            raise ValueError("total_number_of_guests_attending: must be an int")
    else:
        value = 0
    return value


def validate_guest(body: dict) -> Guest:
    """
        Validates the request attributes and creates a guest
    Args:
        body (dict): contains the lambda event info
    Returns:
        Guest: validated Guest
    """
    first_name: str or None = validate_str_section(body, "first_name")
    if first_name is None or first_name == "":
        raise ValueError("first_name: is required")
    last_name: str or None = validate_str_section(body, "last_name")
    if last_name is None or last_name == "":
        raise ValueError("last_name: is required")
    email_address: str or None = validate_str_section(body, "email_address")
    phone_number = validate_phone_number(body, "phone_number")
    total_number_of_guests_attending: int = get_number_of_adults(
        body, "total_number_of_guests_attending"
    )
    try:
        parsed_not_attending = validate_str_section(body, "not_attending")
        if parsed_not_attending is None:
            raise
        not_attending = bool(parsed_not_attending)
    except:
        raise ValueError("not_attending: is required and must be a bool")

    guest: Guest = Guest(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email_address=email_address,
        total_number_of_guests_attending=total_number_of_guests_attending,
        not_attending=not_attending,
    )
    return guest


def insert_update_guest(guest: Guest) -> int:
    """
        Insert or updates the guest in the dynamodb table
    Args:
        guest (Guest): Guest
    Returns:
        int: dynamodb response status code
    """
    table = get_dynamo_db_table()
    dynamodb_response = table.put_item(
        Item={
            "name": guest.first_name_lower + " " + guest.last_name_lower,
            "g_first_name": guest.first_name,
            "g_last_name": guest.last_name,
            "g_email_address": guest.email_address,
            "g_phone_number": guest.phone_number,
            "total_number_of_guests_attending": guest.total_number_of_guests_attending,
            "last_updated": guest.last_updated.strftime("%m-%d-%Y, %H:%M:%S"),
            "not_attending": guest.not_attending,
        }
    )
    return dynamodb_response["ResponseMetadata"]["HTTPStatusCode"]


def get_dynamo_db_table():
    """
        Gets the dynamodb table
    Returns: dynamodb table

    """
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("TABLE_NAME")
    if table_name is None or table_name == "":
        raise ValueError("Unable to get 'TABLE_NAME' variable from environment")
    table = dynamodb.Table(table_name)
    return table
