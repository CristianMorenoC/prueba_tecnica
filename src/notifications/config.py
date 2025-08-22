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

# Environment configuration
EMAIL_TOPIC_ARN = get_env_var('EMAIL_TOPIC_ARN', required=False)
SMS_TOPIC_ARN = get_env_var('SMS_TOPIC_ARN', required=False)
AWS_REGION = get_env_var('AWS_DEFAULT_REGION', 'us-east-1', required=False)