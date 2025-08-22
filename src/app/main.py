from fastapi import FastAPI
from dotenv import load_dotenv
from mangum import Mangum

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Fund Subscription API",
    description="API for managing fund subscriptions and transactions",
    version="1.0.0",
    root_path="/Prod"
)

# Import routes after app creation to avoid circular imports
from routes.routes import *

# Lambda handler
lambda_handler = Mangum(app)
