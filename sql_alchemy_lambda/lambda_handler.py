# We need to have a line similar to this in
# order to always import the models in the
# correct order. It should only be needed
# once when the labda runs. It can be put
# in the lambda handle.
from typing import List, Tuple

# noinspection PyUnresolvedReferences
from sql_alchemy_lambda import dbmodels

import logging
import json
from sqlalchemy.orm import Session
from sql_alchemy_lambda.models.response import Response
from sql_alchemy_lambda.dbmodels import Book, Review
from sql_alchemy_lambda.utilities import get_db_session

logger = logging.getLogger("APP")
logger.setLevel(logging.INFO)

headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}


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
    params = event["queryStringParameters"]

    body = (
        json.loads(event["body"])
        if "body" in event and event["body"] is not None
        else {}
    )
    db_session = get_db_session()
    try:
        if method.upper() == "GET" and route == "book":
            response: dict = get_book(db_session, params)
            logger.info(f"[RESPONSE]: {response}")
            db_session.close()
            return response

        if method.upper() == "POST" and route == "review":
            response: dict = insert_review(db_session, params)
            logger.info(f"[RESPONSE]: {response}")
            db_session.close()
            return response

        response = Response(
            status_code=404, headers={}, body={"message": "{}"}
        ).to_dict()
        logger.info(f"[RESPONSE]: {response}")
        db_session.close()
        return response
    except Exception as e:
        logger.exception(e)
        db_session.close()
        response = Response(
            status_code=500, headers={}, body={"error": e.__str__()}
        ).to_dict()
        logger.info(f"[RESPONSE]: {response}")
        return response


def get_book(db_session: Session, params: dict) -> dict:
    validated_params, errors = validate_get_book_params(params)
    if len(errors.keys()) > 0:
        response: dict = Response(
            status_code=500,
            headers=headers,
            body={"errors": errors},
        ).to_dict()
        return response

    query: Session.query = build_book_query(db_session, params)
    book_results: List[Book] = query.all()
    results = [d.as_dict() for d in book_results]
    response: dict = Response(
        status_code=200,
        headers=headers,
        body={"data": results},
    ).to_dict()
    return response


def validate_get_book_params(params: dict):
    """
    All columns are optional query params, but it validates them if they are included.
    Args:
        params: dict
            query param arguments for the get book endpoint
    Returns:
        dict: validated params
    """
    validated_params = {}
    errors = {}
    if "id" in params and params["id"].strip() is not None and params["id"].strip() != "":
        try:
            validated_params["id"]: int = int(params["id"])
        except:
            errors["id"] = "not a valid integer"
    if "title" in params and params["title"].strip() is not None and params["title"].strip() != "":
        validated_params["title"]: str = params["title"]
    if "author" in params and params["author"].strip() is not None and params["author"].strip() != "":
        validated_params["author"]: str = params["author"]
    if "publisher" in params and params["publisher"].strip() is not None and params["publisher"].strip() != "":
        validated_params["publisher"]: str = params["publisher"]
    if "year" in params and params["year"].strip() is not None and params["year"].strip() != "":
        try:
            validated_params["year"]: int = int(params["year"])
        except:
            errors["year"] = "not a valid integer"
    return validated_params, errors


def build_book_query(db_session: Session, validated_params: dict):
    """

    Args:
        db_session: Session
        validated_params: dict

    Returns:

    """
    query = db_session.query(Book)
    if "id" in validated_params:
        query = query.filter(Book.id == validated_params["id"])
    if "title" in validated_params:
        query = query.filter(Book.title == validated_params["title"])
    if "author" in validated_params:
        query = query.filter(Book.author == validated_params["author"])
    if "publisher" in validated_params:
        query = query.filter(Book.publisher == validated_params["publisher"])
    if "year" in validated_params:
        query = query.filter(Book.year == validated_params["year"])
    return query


def insert_review(db_session: Session, params: dict) -> dict:
    """
        Inserts a new Review
    Args:
        db_session: Session
        params: dict

    Returns:dict

    """
    validated_params, errors = validate_review_params(params)
    if len(errors.keys()) > 0:
        response: dict = Response(
            status_code=500,
            headers=headers,
            body={"errors": json.loads(json.dumps(errors))},
        ).to_dict()
        return response

    review = Review(**validated_params)
    db_session.add(review)
    db_session.commit()
    response: dict = Response(
        status_code=200,
        headers=headers,
        body={"inserted": json.loads(json.dumps(Review.as_dict()))},
    ).to_dict()
    return response


def validate_review_params(params: dict) -> Tuple[dict, dict]:
    """
        validates the review
    Args:
        params: dict

    Returns: dict

    """
    validated_params = {}
    errors = {}
    if "id" in params and params["id"].strip() is not None and params["id"].strip() != "":
        try:
            validated_params["id"]: int = int(params["id"])
        except:
            errors["id"] = "not a valid integer"
    else:
        errors["id"] = "is required and was not included"
    if "reviewer" in params and params["reviewer"].strip() is not None and params["reviewer"].strip() != "":
        validated_params["reviewer"]: str = params["reviewer"]
    else:
        errors["reviewer"] = "is required and was not included"
    if "rate" in params and params["rate"].strip() is not None and params["rate"].strip() != "":
        try:
            validated_params["rate"]: int = int(params["rate"])
        except:
            errors["rate"] = "not a valid integer"
    else:
        errors["rate"] = "is required and was not included"
    if "review" in params and params["review"].strip() is not None and params["review"].strip() != "":
        validated_params["review"]: str = params["review"]
    else:
        errors["review"] = "is required and was not included"
    if "book_id" in params and params["book_id"].strip() is not None and params["book_id"].strip() != "":
        try:
            validated_params["book_id"]: int = int(params["book_id"])
        except:
            errors["book_id"] = "not a valid integer"
    else:
        errors["book_id"] = "is required and was not included"
    return validated_params, errors
