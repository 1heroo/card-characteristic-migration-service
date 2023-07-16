import pandas as pd

from source.char_edit_management.models import Shop
from source.char_edit_management.queries import ShopQueries
from source.char_edit_management.utils import MigrationUtils, WbApiUtils


class MigrationServices:

    def __init__(self):
        self.migration_utils = MigrationUtils()
        self.wb_api_utils = WbApiUtils()

        self.shop_queries = ShopQueries()

    async def migrate_chars(self, df: pd.DataFrame, from_nm_id_column: str, to_nm_id_column: str,
                            from_shop: Shop, to_shop: Shop):

        from_shop_auth = self.wb_api_utils.auth(api_key=from_shop.standard_api_key)
        to_shop_auth = self.wb_api_utils.auth(api_key=to_shop.standard_api_key)

        from_chars_df = await self.get_product_chars_by_nm_ids(
            token_auth=from_shop_auth, nm_ids=list(df[from_nm_id_column]), column_prefix='from')
        to_cars_df = await self.get_product_chars_by_nm_ids(
            token_auth=to_shop_auth, nm_ids=list(df[to_nm_id_column]), column_prefix='to')

        df = df.merge(right=from_chars_df, how='inner', left_on=from_nm_id_column, right_on='from_nm_id')\
            .merge(right=to_cars_df, how='inner', left_on=to_nm_id_column, right_on='to_nm_id')

        products_to_be_imported = []
        for index in df.index:
            from_product: dict = df['from_product'][index]
            to_product: dict = df['to_product'][index]

            to_product['characteristics'] = from_product['characteristics']
            products_to_be_imported.append(to_product)
        await self.wb_api_utils.edit_products(token_auth=to_shop_auth, products=products_to_be_imported)

    async def get_product_chars_by_nm_ids(self, token_auth, nm_ids, column_prefix: str) -> pd.DataFrame:
        products_df = pd.DataFrame([
            {
                'vendor_code': product.get('vendorCode'),
                'nm_id': product.get('nmID')
            }
            for product in await self.wb_api_utils.get_products(token_auth=token_auth)
        ])
        df = pd.merge(pd.DataFrame(nm_ids, columns=['nm_id']), products_df, how='inner', on='nm_id')
        products = await self.wb_api_utils.get_chars_by_vendor_codes(vendor_codes=list(df['vendor_code']), token_auth=token_auth)
        return pd.DataFrame([
            {f'{column_prefix}_product': product, f'{column_prefix}_nm_id': product.get('nmID')}
            for product in products
        ])

