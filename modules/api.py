import asyncio

import aiohttp


class Api:
    def __init__(self, hostname, port, protocol):
        self._endpoint = f"{protocol}://{hostname}:{port}"
        self._loop = asyncio.get_event_loop()

    async def _async_get(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self._endpoint) as response:
                    return await response.json()
            except aiohttp.ClientConnectorError as error:
                print('Connection Error', str(error))
                raise error

    def get(self):
        return self._loop.run_until_complete(self._async_get())
