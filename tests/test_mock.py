# coding: utf-8
import asyncio

from echod.mock import Mock


async def test_mock_client():
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
    async with Mock(expectation) as client:
        return await client.health()


loop = asyncio.get_event_loop()
loop.run_until_complete(test_mock_client())
loop.close()
