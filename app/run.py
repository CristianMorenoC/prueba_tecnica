from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Fund Subscription API",
    description="API for managing fund subscriptions and transactions",
    version="1.0.0"
)

# Import development routes
from app.routes import routes_dev