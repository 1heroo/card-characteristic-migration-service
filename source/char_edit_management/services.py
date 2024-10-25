import pandas as pd

from source.char_edit_management.models import Shop
from source.char_edit_management.queries import ShopQueries
from source.char_edit_management.utils import MigrationUtils, WbApiUtils


class MigrationServices:

    def __init__(self):
        self.migration_utils = MigrationUtils()
        self.wb_api_utils = WbApiUtils()

        self.shop_queries = ShopQueries()

    async def migrate_chars(self, df: pd.DataFrame, from_nm_id_column: str,
                            to_nm_id_column: str,
                            from_shop: Shop, to_shop: Shop):

        from_shop_auth = self.wb_api_utils.auth(api_key=from_shop.standard_api_key)
        to_shop_auth = self.wb_api_utils.auth(api_key=to_shop.standard_api_key)

        from_chars_df = await self.get_product_chars_by_nm_ids(
            token_auth=from_shop_auth, nm_ids=list(df[from_nm_id_column]), column_prefix='from')
        to_chars_df = await self.get_product_chars_by_nm_ids(
                token_auth=to_shop_auth, nm_ids=list(df[to_nm_id_column]), column_prefix='to')

        df = df.merge(right=from_chars_df, how='inner', left_on=from_nm_id_column, right_on='from_nm_id')\
            .merge(right=to_chars_df, how='inner', left_on=to_nm_id_column, right_on='to_nm_id')

        products_to_be_imported = []
        images_to_be_updated = []

        for index in df.index:
            from_product: dict = df['from_product'][index]
            to_product: dict = df['to_product'][index]

            to_product['characteristics'] = from_product['characteristics']
            to_product['title'] = from_product['title']
            to_product['brand'] = from_product['brand']
            print(to_product['brand'], from_product['brand'])
            to_product['description'] = from_product['description']
            to_product['dimensions'] = from_product['dimensions']
            products_to_be_imported.append(to_product)

            img_obj = {
                'nmId': to_product.get('nmID'),
                'data': [
                    photo.get('big')
                    for photo in from_product.get('photos', [])
                ]
            }
            video = from_product.get('video')
            if video:
                img_obj['data'].append(video)

            images_to_be_updated.append(img_obj)

        unique_vendor_codes = []
        unique_products = []
        duplicated_products = []

        for product in products_to_be_imported:
            vendor_code = product.get('vendorCode')
            if vendor_code in unique_vendor_codes:
                duplicated_products.append(product)
            else:
                unique_vendor_codes.append(vendor_code)
                unique_products.append(product)

        print(len(unique_products))
        print(len(duplicated_products))
        print(unique_products)
        print(images_to_be_updated)
        await self.wb_api_utils.edit_products(token_auth=to_shop_auth, products=unique_products)
        await self.wb_api_utils.edit_products(token_auth=to_shop_auth, products=duplicated_products)

        for img_obj in images_to_be_updated:
            await self.wb_api_utils.change_images(img_obj, token_auth=to_shop_auth)

    async def get_product_chars_by_nm_ids(self, token_auth, nm_ids, column_prefix: str) -> pd.DataFrame:
        products_df = pd.DataFrame([
            {
                'product': product,
                'nm_id': int(product.get('nmID', 0))
            }
            for product in await self.wb_api_utils.get_products(token_auth=token_auth)
        ], columns=['product', 'nm_id'])

        products_df = products_df[products_df['nm_id'].isin(nm_ids)]
        return pd.DataFrame([
            {f'{column_prefix}_product': product, f'{column_prefix}_nm_id': product.get('nmID')}
            for product in products_df['product']
        ])

    async def migrate_chars_full_shop(self, from_shop: Shop, to_shop: Shop, brands):
        from_shop_auth = self.wb_api_utils.auth(api_key=from_shop.standard_api_key)
        to_shop_auth = self.wb_api_utils.auth(api_key=to_shop.standard_api_key)

        from_chars = await self.wb_api_utils.get_products(token_auth=from_shop_auth, brands=brands)
        to_chars = await self.wb_api_utils.get_products(token_auth=to_shop_auth, brands=brands)

        from_chars_df = pd.DataFrame(list(map(lambda item: {'from_vendor_code': item.get('vendorCode'), 'from_product': item}, from_chars)))
        to_chars_df = pd.DataFrame(list(map(lambda item: {'to_vendor_code': item.get('vendorCode'), 'to_product': item}, to_chars)))
        df = pd.merge(from_chars_df, to_chars_df, how='inner', left_on='from_vendor_code', right_on='to_vendor_code')

        df = df.drop_duplicates(subset=['to_vendor_code'])
        print(df)
        products = []
        for index in df.index:
            from_product: dict = df['from_product'][index]
            to_product: dict = df['to_product'][index]

            to_product['characteristics'] = from_product.get('characteristics')
            to_product['description'] = from_product.get('description')
            to_product['dimensions'] = from_product.get('dimensions')
            to_product['title'] = from_product.get('title')
            products.append(to_product)

            images = [item['big'] for item in from_product.get('photos', [])]

            if len(images) != len(to_product.get('photos', [])) and len(images) != 0:
                await self.wb_api_utils.change_images(vendor_code=to_product.get('vendorCode'), token_auth=to_shop_auth, images_list=images)
            print(index)

        await self.wb_api_utils.edit_products(token_auth=to_shop_auth, products=products)

    async def get_all_product_chars(self, token_auth, column_prefix: str, brands = None) -> pd.DataFrame:
        products = await self.wb_api_utils.get_products(token_auth=token_auth)
        if brands:
            products = [product for product in products if product.get('brand') in brands]

        products_df = pd.DataFrame([
            {
                'vendor_code': product.get('vendorCode'),
                'nm_id': product.get('nmID')
            }
            for product in products
        ])

        products = await self.wb_api_utils.get_chars_by_vendor_codes(vendor_codes=list(products_df['vendor_code']), token_auth=token_auth)
        return pd.DataFrame([
            {f'{column_prefix}_product': product, f'{column_prefix}_vendor_code': product.get('vendorCode')}
            for product in products
        ])

    async def define_brand_by_chars(self, characteristics: list[dict]):
        for char in characteristics:
            for name, value in char.items():
                if name == 'Бренд':
                    return value

    async def create_products_in_shop(self, from_shop: Shop, to_shop: Shop, df: pd.DataFrame, nm_id_column: str):
        print(df)
