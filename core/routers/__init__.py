from .admin           import router as admin_router
from .auth_users      import router as auth_users_router
from .chat            import router as chat_router
from .gaians          import router as gaians_router
from .health          import router as health_router
from .internal_router import router as internal_router
from .memory          import router as memory_router
from .mood_ws         import router as mood_ws_router
from .query           import router as query_router
from .room            import router as room_router
from .system          import router as system_router
from .zodiac          import router as zodiac_router

__all__ = [
    "admin_router",
    "auth_users_router",
    "chat_router",
    "gaians_router",
    "health_router",
    "internal_router",
    "memory_router",
    "mood_ws_router",
    "query_router",
    "room_router",
    "system_router",
    "zodiac_router",
]
