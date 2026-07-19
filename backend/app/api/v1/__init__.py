from fastapi import APIRouter

from app.api.v1 import admin_products, auth, cart, checkout, contact, products

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(checkout.router)
api_router.include_router(contact.router)
api_router.include_router(auth.router)
api_router.include_router(admin_products.router)
