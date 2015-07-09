echo
====

Echo is a fully configurable mock server, TCP chaos monkey proxy and an HTTP
callback recorder. It is perfect to test external services.

The Echo make extensive use of Python context managers. This make it easy
to controlling Echo on the fly from your code or using your testing framework
setup mechanism.

The main part of Echo is an HTTP server with an REST API, the Echo HTTP server
have a lot of flexibility and support many start up methods.

Echo server can be run as:

* A standalone using `echo` command line tool.
* A WSGI HTTP Server application.
* A Docker instance container.


Mock
----

```python
import echo


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

with echo.mock(**expectation) as client:
    response = client.post()
    response.status_code == 200
```


Proxy
-----

```python
import settings


expectation = {
    'backend': 'google.com:80',
    'behaviour': {'20:delay': {'before': True, 'sleep': 1}},
    'protocol': {'http': {'buffer': 8124, 'keep_alive': False,
                          'overwrite_host_header': True,
                          'reuse_socket': False}}
}

with echo.proxy(**expectation) as proxy:
    settings.external_service_url = proxy.url
    proxy.post()
```


callback
--------

```python
import requests


with echo.callback() as webhook:
    settings.callback_url = webhook.url
    requests.post()
    webhook.wait_callback(timeout=10)
    webhook.response.data == {...}
```
