from fastapi import APIRouter
from source.char_edit_management.routes import router as migration_router


router = APIRouter(prefix='/api/v1')

router.include_router(router=migration_router)

