import pandas as pd
from fastapi import APIRouter, File
from starlette import status
from starlette.responses import JSONResponse, Response, PlainTextResponse

from source.char_edit_management.services import MigrationServices

migration_services = MigrationServices()


router = APIRouter(prefix='/characteristic-migration')


@router.post('/migrate-characteristics/{from_shop_id}/{to_shop_id}')
async def migrate_characteristics(from_shop_id: int, to_shop_id: int, file: bytes = File()):
    df = pd.read_excel(file)
    from_nm_id_column = df['Артикул WB 1'].name
    to_nm_id_column = df['Артикул WB 2'].name
    df = df.dropna(subset=[from_nm_id_column, to_nm_id_column])
    df = df.drop_duplicates(subset=[from_nm_id_column])

    from_shop = await migration_services.shop_queries.get_shop_by_id(shop_id=from_shop_id)
    to_shop = await migration_services.shop_queries.get_shop_by_id(shop_id=to_shop_id)

    if from_shop is None or to_shop is None:
        return JSONResponse(content={'message': 'Один из магазинов не найден'}, status_code=status.HTTP_404_NOT_FOUND)

    await migration_services.migrate_chars(
        df=df, from_shop=from_shop, to_shop=to_shop, from_nm_id_column=from_nm_id_column, to_nm_id_column=to_nm_id_column)

    return PlainTextResponse(
        content=f'С магазина {from_shop.title} на магазин {to_shop.title} характеристики введенных товаров успешно перенесены')


@router.post('/migrate-characteristics/{from_shop_id}/{to_shop_id}/full-shop')
async def migrate_chars(from_shop_id: int, to_shop_id: int, brands: str = None):
    from_shop = await migration_services.shop_queries.get_shop_by_id(shop_id=from_shop_id)
    to_shop = await migration_services.shop_queries.get_shop_by_id(shop_id=to_shop_id)

    if from_shop is None or to_shop is None:
        return JSONResponse(content={'message': 'Один из магазинов не найден'}, status_code=status.HTTP_404_NOT_FOUND)

    if brands:
        brands = brands.split(', ')

    await migration_services.migrate_chars_full_shop(from_shop=from_shop, to_shop=to_shop, brands=brands)

    return PlainTextResponse(
        content=f'С магазина {from_shop.title} на магазин {to_shop.title} характеристики введенных товаров успешно перенесены')
