import json
from unittest.mock import patch
from sql_alchemy_lambda.dbmodels import Book
from sql_alchemy_lambda.lambda_handler import get_book


@patch('sql_alchemy_lambda.lambda_handler.build_book_query')
@patch('sql_alchemy_lambda.lambda_handler.validate_get_book_params')
@patch('sql_alchemy_lambda.lambda_handler.Session')
def test_get_book(mock_session, mock_validate_get_book_params, mock_build_book_query):
    validated_params = {
        "id": 1,
        "title": "The Title",
        "author": "Joe Smith",
        "publisher": "Bobby Jones",
        "year": 1965
    }
    mock_validate_get_book_params.return_value = (validated_params, {})
    book = Book(**validated_params)
    mock_build_book_query.return_value.all.return_value = [book]
    expected = {
        "statusCode": 200,
        'isBase64Encoded': False,
        "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            }
        ,
        "body": {"data": json.loads(json.dumps([
            {'author': 'Joe Smith',
             'id': 1,
             'publisher': 'Bobby Jones',
             'title': 'The Title',
             'year': 1965}
        ]))}
    }
    result = get_book(mock_session, validated_params)
    assert "body" in result
    assert expected["statusCode"] == result["statusCode"]
    assert expected["isBase64Encoded"] == result["isBase64Encoded"]
    assert expected["headers"] == result["headers"]

    for (res, exp) in zip(result["body"]["data"], expected["body"]["data"]):
        assert res["author"] == exp["author"]
        assert res["id"] == exp["id"]
        assert res["publisher"] == exp["publisher"]
        assert res["title"] == exp["title"]
        assert res["year"] == exp["year"]