from source.core.utils import BaseUtils


class MigrationUtils(BaseUtils):
    pass


class WbApiUtils(BaseUtils):

    @staticmethod
    def auth(api_key: str) -> dict:
        return {
            'Authorization': api_key
        }

    async def get_products(self, token_auth: dict, brands: list[str] = []) -> list[dict]:
        data = []
        url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
        payload = {
            "settings": {
                "cursor": {
                    "limit": 100
                },
                "filter": {
                    "withPhoto": -1,
                    'brands': brands
                }
            }
        }

        while True:
            partial_data = await self.make_post_request(headers=token_auth, url=url, payload=payload)
            if partial_data is None:
                return data

            data += partial_data['cards']
            payload['settings']['cursor']['updatedAt'] = partial_data['cursor']['updatedAt']
            payload['settings']['cursor']['nmID'] = partial_data['cursor']['nmID']
            if partial_data['cards'].__len__() < 100:
                break
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

    async def edit_products(self, products: list[dict], token_auth: dict):
        url = 'https://content-api.wildberries.ru/content/v2/cards/update'
        for index in range(0, len(products), 3000):
            await self.make_post_request(url=url, headers=token_auth, payload=products[index: index + 3000], print_data=True)

    async def change_images(self, image_obj: dict, token_auth: dict):
        url = 'https://content-api.wildberries.ru/content/v3/media/save'
        await self.make_post_request(url=url, headers=token_auth, payload=image_obj, print_data=True)
