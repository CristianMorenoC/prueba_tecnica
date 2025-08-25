from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from mangum import Mangum

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Fund Subscription API",
    description="API for managing fund subscriptions and transactions - v2.0 WITH CONTACT INFO FIX",
    version="2.0.0",
    root_path="/Prod"
)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

# Import routes after app creation to avoid circular imports
from routes.routes import *

# Lambda handler
lambda_handler = Mangum(app)
