# coding: utf-8

from echod.forms import RequestForm, ResponseForm, MockForm


def test_request_form():
    data = {
        'body': {
            'name': 'John Doe'
        },
        'headers': {
            'content_type': 'application/json',
            'accept': 'application/json'
        }
    }
    form = RequestForm(data=data)
    assert form.validate()


def test_response_form():
    data = {
        'body': {
            'name': 'John Doe'
        },
        'headers': {
            'content_type': 'application/json',
            'accept': 'application/json'
        },
        'status_code': 201,
    }
    form = ResponseForm(data=data)
    assert form.validate()


def test_mock_form():
    data = {
        'method': 'PUT',
        'path': '/v1/users/',
        'request': {
            'body': {
                'name': 'John Doe'
            },
            'headers': {
                'content_type': 'application/json',
                'accept': 'application/json'
            }
        },
        'response': {
            'body': {
                'name': 'John Doe'
            },
            'headers': {
                'content_type': 'application/json',
                'accept': 'application/json'
            },
            'status_code': 201,
        }
    }
    form = MockForm(data=data)
    assert form.validate()


def test_mock_form_without_request():
    data = {
        'method': 'PUT',
        'path': '/v1/users/',
        'response': {
            'body': {
                'name': 'John Doe'
            },
            'headers': {
                'content_type': 'application/json',
                'accept': 'application/json'
            },
            'status_code': 201,
        }
    }
    form = MockForm(data=data)
    assert form.validate()
