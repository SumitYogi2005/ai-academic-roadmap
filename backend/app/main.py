from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import health


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered academic roadmap and personalized study planner",
    debug=settings.DEBUG
)


# Register API routers
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX
)


@app.get("/")
def root():

    return {
        "message": "Welcome to AI Academic Roadmap API",
        "version": settings.APP_VERSION,
        "documentation": "/docs"
    }