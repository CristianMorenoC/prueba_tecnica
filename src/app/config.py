import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

def get_env_var(name: str, default: str = None, required: bool = True) -> str:
    """
    Get environment variable with optional default and validation
    
    Args:
        name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        str: Environment variable value
        
    Raises:
        ValueError: If required variable is not found
    """
    value = os.environ.get(name, default)
    
    if required and not value:
        raise ValueError(f"{name} environment variable is required")
    
    return value

# Detect if we're running in AWS Lambda or local environment
IS_LOCAL = not bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

# DynamoDB Configuration
APPCHALLENGE_TABLE_NAME = get_env_var('APPCHALLENGE_TABLE_NAME', 'AppChallenge', required=False)
APPCHALLENGE_TABLE_ARN = get_env_var('APPCHALLENGE_TABLE_ARN', required=False)

# AWS Configuration
AWS_REGION = get_env_var('AWS_DEFAULT_REGION', 'us-east-1', required=False)
AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID', required=False)
AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY', required=False)

# AWS operations enabled only in Lambda environment or when credentials are available
AWS_OPERATIONS_ENABLED = not IS_LOCAL or (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)