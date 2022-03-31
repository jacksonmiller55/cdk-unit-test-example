import json
import os

from lambdaCode.models.response import Response


def test_response_from_code():
    exp_status_code = 200
    exp_headers = {"some": "fake_headers"}
    exp_body = {"some": "fake", "body": {"info": None}}

    exp_to_dict = {
        "body": '{"some": "fake", "body": {"info": null}}',
        "headers": {"some": "fake_headers"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    response = Response(
        exp_status_code,
        exp_headers,
        exp_body,
    )
    assert response.isBase64Encoded == False
    assert response.statusCode == exp_status_code
    assert response.headers == exp_headers
    assert response.body == exp_body
    assert response.to_dict() == exp_to_dict


def test_response_from_file():
    exp_status_code = 200
    exp_headers = {"some": "fake_headers"}
    exp_body = {"some": "fake", "info": None}

    exp_to_dict = {}
    dirname = os.path.dirname(__file__)
    response_to_dict_path = os.path.join(dirname, "test_files/response_to_dict.json.json")
    with open(response_to_dict_path, 'r') as f:
        data = f.read()
        exp_to_dict = json.loads(data)

    response = Response(
        exp_status_code,
        exp_headers,
        exp_body,
    )
    assert response.isBase64Encoded == False
    assert response.statusCode == exp_status_code
    assert response.headers == exp_headers
    assert response.body == exp_body
    j = response.to_dict()
    assert response.to_dict() == exp_to_dict

    # This is not the prettiest way to do it. There has to be a better way.
    # (null vs None) when reading json directly from a file starts to be a problem.
    # This is just a work around since you are doing the same json.loads and json.dumps to each.
    assert json.loads(json.dumps(response.to_dict())) == json.loads(json.dumps(exp_to_dict))
