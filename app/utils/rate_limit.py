"""
Rate limiting utilities for API endpoints.
Uses slowapi to prevent brute force attacks and API abuse.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.
    Uses forwarded IP if behind proxy, otherwise remote address.
    
    Args:
        request: FastAPI request object
    
    Returns:
        str: Client identifier (IP address)
    """
    # Check for forwarded IP (if behind reverse proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get first IP in chain (original client)
        return forwarded.split(",")[0].strip()
    
    # Fall back to direct remote address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=["100/hour"],  # Default rate limit for all endpoints
    storage_uri="memory://"  # Use in-memory storage (for production, consider Redis)
)


# Rate limit configurations for specific use cases
RATE_LIMITS = {
    "login": "5/minute",  # Allow only 5 login attempts per minute per IP
    "upload": "20/hour",  # Allow 20 uploads per hour per IP
    "delete": "30/hour",  # Allow 30 deletions per hour per IP
    "general": "100/hour",  # General API operations
}

