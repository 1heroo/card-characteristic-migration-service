from fastapi import FastAPI

from source.char_edit_management.admin import ShopAdmin
from source.db.db import async_engine
import uvicorn
from sqladmin import Admin
from source.core.routes import router


app = FastAPI(title='Перенос харакеристик карточки WB')


app.include_router(router=router)


admin = Admin(app=app, engine=async_engine)

admin.add_view(ShopAdmin)


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        port=8000,
        host='0.0.0.0',
        reload=True
    )
