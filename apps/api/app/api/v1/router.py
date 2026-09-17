from fastapi import APIRouter

from app.api.v1 import auth, catalogs, people, receipts, sync, tenant_config, tenants, users, work_orders

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(tenant_config.router)
api_router.include_router(users.router)
api_router.include_router(catalogs.asset_types_router)
api_router.include_router(catalogs.work_order_types_router)
api_router.include_router(catalogs.priorities_router)
api_router.include_router(catalogs.work_order_statuses_router)
api_router.include_router(people.customers_router)
api_router.include_router(people.technicians_router)
api_router.include_router(people.locations_router)
api_router.include_router(people.assets_router)
api_router.include_router(work_orders.router)
api_router.include_router(receipts.router)
api_router.include_router(sync.router)
