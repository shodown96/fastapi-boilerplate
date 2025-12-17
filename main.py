from api import api_router
from core.setup import create_application
from core.config import settings

app = create_application(router=api_router, settings=settings)
