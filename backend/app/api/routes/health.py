from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def health_check():

    return {
        "status": "success",
        "message": "AI Academic Roadmap Backend is running!",
        "service": "FastAPI"
    }


@router.get("/welcome")
def welcome():

    return {
        "message": "Welcome to AI Academic Roadmap",
        "description": "Your personalized AI-powered learning platform."
    }