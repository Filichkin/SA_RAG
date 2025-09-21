from fastapi import APIRouter

from app.api.endpoints import (
    user_router,
    two_factor_auth
)


main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(two_factor_auth.router)
