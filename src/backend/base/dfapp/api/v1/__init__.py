from dfapp.api.v1.api_key import router as api_key_router
from dfapp.api.v1.chat import router as chat_router
from dfapp.api.v1.endpoints import router as endpoints_router
from dfapp.api.v1.files import router as files_router
from dfapp.api.v1.flows import router as flows_router
from dfapp.api.v1.login import router as login_router
from dfapp.api.v1.monitor import router as monitor_router
from dfapp.api.v1.store import router as store_router
from dfapp.api.v1.users import router as users_router
from dfapp.api.v1.validate import router as validate_router
from dfapp.api.v1.variable import router as variables_router

__all__ = [
    "chat_router",
    "endpoints_router",
    "store_router",
    "validate_router",
    "flows_router",
    "users_router",
    "api_key_router",
    "login_router",
    "variables_router",
    "monitor_router",
    "files_router",
]
