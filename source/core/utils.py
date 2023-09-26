import aiohttp
import json


class BaseUtils:

    @staticmethod
    async def make_get_request(url, headers):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            async with session.get(url=url) as response:
                print(response.status)
                if response.status == 200:
                    return json.loads(await response.text())

    @staticmethod
    async def make_post_request(url, headers, payload):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            async with session.post(url=url, json=payload) as response:
                print(response.status)
                if response.status == 200:
                    return json.loads(await response.text())

    @staticmethod
    async def make_fast_get_request(url, session: aiohttp.ClientSession):
        response = await session.get(url=url)

        if response.status == 200:
            return json.loads(await response.text())
