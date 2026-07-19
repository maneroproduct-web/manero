from fastapi import APIRouter

from app.api.v1 import cart, checkout, products

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(checkout.router)
