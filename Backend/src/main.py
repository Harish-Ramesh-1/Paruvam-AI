from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.api_routes import router

app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# Register routes
app.include_router(router)