from lambdaCode.models.response import Response


def test_response():
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
