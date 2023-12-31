from source.core.utils import BaseUtils


class MigrationUtils(BaseUtils):
    pass


class WbApiUtils(BaseUtils):

    @staticmethod
    def auth(api_key: str) -> dict:
        return {
            'Authorization': api_key
        }

    async def get_products(self, token_auth: dict) -> list[dict]:
        data = []
        url = 'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list'
        payload = {
            "sort": {
                "cursor": {
                    "limit": 1000
                },
                "filter": {
                    "withPhoto": -1
                }
            }
        }
        total = 1
        while total != 0:
            partial_data = await self.make_post_request(headers=token_auth, url=url, payload=payload)
            if partial_data is None:
                return data

            data += partial_data['data']['cards']
            cursor = partial_data['data']['cursor']
            payload['sort']['cursor'].update(cursor)
            total = cursor['total']
        return data

    async def get_chars_by_vendor_codes(self, token_auth: dict, vendor_codes: list[dict]):
        url = 'https://suppliers-api.wildberries.ru/content/v1/cards/filter'
        output_data = []

        for index in range(0, len(vendor_codes), 100):
            payload = {"vendorCodes": vendor_codes[index: index + 100], "allowedCategoriesOnly": False}
            data = await self.make_post_request(headers=token_auth, payload=payload, url=url)
            if data:
                output_data += data.get('data', [])
        return output_data

    async def edit_products(self, token_auth: dict, products: list[dict]):
        url = 'https://suppliers-api.wildberries.ru/content/v1/cards/update'

        for index in range(0, len(products), 1000):
            chunk_products = products[index: index + 1000]
            data = await self.make_post_request(payload=chunk_products, headers=token_auth, url=url)
            print(data)

    async def change_images(self, vendor_code: str, token_auth: dict, images_list):
        url = 'https://suppliers-api.wildberries.ru/content/v1/media/save'
        payload = {
            "vendorCode": vendor_code,
            "data": images_list
        }
        print(await self.make_post_request(url=url, headers=token_auth, payload=payload))
