# coding: utf-8

from echod.mock import Mock


def test_mock_client():
    expectation = {
        'method': 'POST',
        'path': '/v1/users/',
        'request': {'body': {'email': 'john@doe.com',
                             'name': 'John Doe',
                             'password': 'secret'},
                    'headers': {'accept': 'application/json',
                                'content_type': 'application/json'}},
        'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                     'headers': {'content_type': 'application/json'},
                     'status_code': 201}
    }
    with Mock(expectation) as client:
        assert client.response() == 'Ok'
