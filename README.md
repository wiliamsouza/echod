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
import echod


mock_response = {
    'status_code': 200,
    'body': {...},
}

request_contain = {
    'body': {...}
}

expectation = {
    'method': 'POST',
    'path': '/v1/users/',
    'request': request_contain,
    'response': mock_response,
}

with echod.mock(**expectation) as client:
    response = client.post()
    response.status_code == 200
```


callback
--------

```python
import requests


with echod.callback() as webhook:
    settings.callback_url = webhook.url
    requests.post()
    webhook.wait_callback(timeout=10)
    webhook.response.data == {...}
```
