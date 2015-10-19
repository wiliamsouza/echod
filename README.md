echod
=====

[![Build Status](https://travis-ci.org/wiliamsouza/echo.svg)](https://travis-ci.org/wiliamsouza/echo)
[![Coverage Status](https://coveralls.io/repos/wiliamsouza/echo/badge.svg?branch=master&service=github)](https://coveralls.io/github/wiliamsouza/echo?branch=master)

Echod is a fully configurable mock server and an HTTP callback recorder. It is
perfect to test external services.

It is easy to controlling Echod on the fly from your code or using your testing
framework setup mechanism.

The main part of Echod is an HTTP server with an REST API, the Echo HTTP server
have a lot of flexibility and support many start up methods.

Echod server can be run as:

* A standalone using `echod` command line tool.
* A WSGI HTTP Server application.
* A Docker instance container.


Mock
----

```python
from echod.mock import Mock

# This will create a mock that accepts `POST` in the path `/v1/users/`.
expectation = {
    'method': 'POST',
    'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                 'headers': {'content_type': 'application/json'},
                 'status_code': 201}
}

with Mock(expectation) as client:
    # The mock URL is available to use
    client.mock_url  # 'http://127.0.0.1:9876/mock/fbf01f94169640de9e585fe5e30a0958/'

    # This method will make a request to the mock
    response = client.response()
    assert response.status_code == 201
```
