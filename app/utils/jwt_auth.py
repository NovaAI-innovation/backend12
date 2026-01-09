"""
JWT Token-based authentication utilities for CMS access.
Provides secure token generation, verification, and session management.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Header, Request
from app.config import settings
from app.utils.auth import verify_admin_password


# JWT Configuration
SECRET_KEY = settings.JWT_SECRET_KEY  # Will need to add to config
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expires after 1 hour


class TokenData:
    """Data structure for JWT token payload"""
    def __init__(self, role: str = "admin", exp: Optional[datetime] = None):
        self.role = role
        self.exp = exp


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of claims to include in token
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid token type", "message": "Token is not an access token"}
            )
        
        # Check if token is expired (jose should handle this, but double-check)
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            if datetime.now(timezone.utc) > exp_datetime:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"error": "Token expired", "message": "Please login again"}
                )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid token", "message": "Authentication token is invalid or expired"}
        )


def verify_cms_token(
    request: Request,
    authorization: Optional[str] = Header(None, description="Bearer token for authentication (fallback to cookie)")
) -> dict:
    """
    FastAPI dependency for JWT token authentication.
    Verifies the Bearer token from httpOnly cookie (preferred) or Authorization header (fallback).
    httpOnly cookies prevent XSS attacks (NFR-S3, FR55).
    
    Args:
        request: FastAPI request object (for reading cookies)
        authorization: Authorization header value (e.g., "Bearer <token>") - optional fallback
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    token = None
    
    # Priority 1: Check httpOnly cookie (preferred for security)
    token = request.cookies.get("cms_token")
    
    # Priority 2: Fallback to Authorization header (for compatibility)
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    
    # No token found in cookie or header
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Missing token", "message": "Authentication required"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return verify_token(token)


def authenticate_user(password: str) -> dict:
    """
    Authenticate user with password and return token data.
    
    Args:
        password: Plain text password to verify
    
    Returns:
        dict: Token payload data if authentication successful
    
    Raises:
        HTTPException: 401 if password is invalid
    """
    if not verify_admin_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid credentials", "message": "Incorrect password"}
        )
    
    # Return token data
    return {
        "role": "admin",
        "sub": "cms_admin"  # Subject (user identifier)
    }

