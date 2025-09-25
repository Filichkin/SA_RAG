from fastapi import APIRouter

from app.api.endpoints import (
    ai_agent_router,
    two_factor_auth,
    user_router
)


main_router = APIRouter()

main_router.include_router(ai_agent_router)
main_router.include_router(two_factor_auth)
main_router.include_router(user_router)
