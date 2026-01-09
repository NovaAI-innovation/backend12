# CMS Authentication Security

## Overview

The CMS now uses **JWT (JSON Web Token) authentication** instead of plain password transmission. This provides a significantly safer authentication mechanism with multiple security enhancements.

## Security Improvements

### ✅ What Changed

| **Before** | **After** |
|-----------|----------|
| Password stored in `sessionStorage` | JWT token stored in `sessionStorage` |
| Password sent with every request | Token sent with every request |
| No expiration | 1-hour token expiration |
| No rate limiting | 5 login attempts per minute per IP |
| Vulnerable to XSS attacks | Better protection (token can't be reused to login) |

### 🔒 Security Features

1. **JWT Token Authentication**
   - Password exchanged for a time-limited token
   - Token expires after 1 hour (configurable)
   - Token includes role and expiration claims
   - Uses HS256 algorithm with secret key

2. **Rate Limiting**
   - **Login endpoint**: 5 attempts/minute per IP
   - **Upload endpoint**: 20 uploads/hour per IP (configured)
   - **Delete endpoint**: 30 deletions/hour per IP (configured)
   - Prevents brute force attacks

3. **Automatic Session Management**
   - Auto-logout when token expires
   - Warning 5 minutes before expiration
   - Token validation on every request

4. **Secure Password Handling**
   - Password never stored (only hashed)
   - Password only transmitted during login
   - Bcrypt hashing with salt

## Setup Instructions

### 1. Generate Secret Key

Generate a strong secret key for JWT signing:

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### 2. Update Environment Variables

Add to your `.env` file:

```env
# JWT Configuration
JWT_SECRET_KEY=your-generated-secret-key-here

# Admin Password Hash (use the hash generation script)
ADMIN_PASSWORD_HASH=your-bcrypt-hashed-password
```

### 3. Generate Password Hash

Create a Python script to hash your admin password:

```python
# hash_password.py
import bcrypt

password = input("Enter admin password: ")
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(f"\nADMIN_PASSWORD_HASH={hashed.decode('utf-8')}")
```

Run it:
```bash
cd backend12
uv run hash_password.py
```

Copy the output to your `.env` file.

## API Usage

### Login Endpoint

**POST** `/api/cms/login`

Request:
```json
{
  "password": "your-admin-password"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Protected Endpoints

All CMS endpoints now require the JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGc...
```

Example:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/cms/gallery-images
```

## Frontend Implementation

The frontend (`cms.js`) has been updated to:

1. **Login Flow**
   - POST password to `/api/cms/login`
   - Store token in sessionStorage
   - Calculate expiry time

2. **API Requests**
   - Include `Authorization: Bearer <token>` header
   - Handle 401 (Unauthorized) responses
   - Redirect to login on token expiry

3. **Session Management**
   - Auto-logout when token expires
   - Show warning 5 minutes before expiration
   - Clear token on logout

## Security Best Practices

### ✅ Recommended

1. **Use HTTPS in production** - Protect tokens in transit
2. **Keep JWT_SECRET_KEY secret** - Never commit to version control
3. **Use strong admin passwords** - 16+ characters, mixed case, symbols
4. **Rotate secret keys periodically** - Every 90 days in production
5. **Monitor rate limit violations** - Check logs for suspicious activity
6. **Consider Redis for rate limiting** - For multi-instance deployments

### ❌ Avoid

1. **Don't use HTTP in production** - Tokens can be intercepted
2. **Don't share JWT_SECRET_KEY** - Compromises all tokens
3. **Don't store tokens in localStorage** - More vulnerable to XSS than sessionStorage
4. **Don't disable rate limiting** - Opens door to brute force attacks
5. **Don't use weak passwords** - Easy to guess/crack

## Advanced Configuration

### Customize Token Expiration

Edit `backend12/app/utils/jwt_auth.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Change from 60 to 120 minutes
```

### Customize Rate Limits

Edit `backend12/app/utils/rate_limit.py`:

```python
RATE_LIMITS = {
    "login": "10/minute",  # Increase from 5 to 10
    "upload": "50/hour",   # Increase from 20 to 50
    "delete": "60/hour",   # Increase from 30 to 60
}
```

### Use Redis for Rate Limiting

For production with multiple server instances:

```python
# In app/utils/rate_limit.py
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri="redis://localhost:6379"  # Change from memory://
)
```

## Troubleshooting

### Token Expired Error

**Symptom**: Getting 401 errors after 1 hour

**Solution**: Login again to get a new token. This is expected behavior.

### Rate Limit Exceeded

**Symptom**: Getting 429 errors when logging in

**Solution**: Wait 1 minute before trying again. This protects against brute force attacks.

### Invalid Token Error

**Symptom**: 401 error immediately after login

**Solution**: 
1. Check JWT_SECRET_KEY is set correctly
2. Verify token is being sent in correct format: `Bearer <token>`
3. Check server and client clocks are synchronized

## Migration Guide

### From Old System to New System

1. **Backend Changes**
   - JWT dependencies installed automatically
   - All CMS routes updated to use JWT
   - Login endpoint added at `/api/cms/login`
   - Rate limiting added to login endpoint

2. **Frontend Changes**
   - `cmsState.password` → `cmsState.accessToken`
   - `X-CMS-Password` header → `Authorization: Bearer` header
   - Login flow calls `/api/cms/login` first
   - Auto-logout on token expiration

3. **No User Action Required**
   - Users will be prompted to login again
   - Their password still works the same
   - Session will now expire after 1 hour (more secure)

## Security Considerations

### Still Using sessionStorage?

Yes, but it's safer now because:
- Storing a **time-limited token** instead of the actual password
- Token can't be used to login again (need password for that)
- Token expires automatically
- If token is stolen, damage window is limited to 1 hour

### Future Enhancements (Optional)

For even better security, consider:

1. **HTTP-only cookies** - Immune to XSS attacks
2. **Refresh tokens** - Long-lived, allows token renewal
3. **2FA (Two-Factor Auth)** - Additional security layer
4. **IP whitelisting** - Restrict CMS access by IP
5. **Audit logging** - Track all CMS operations

## Questions?

For issues or questions about the authentication system:
1. Check this document first
2. Review the code comments in `app/utils/jwt_auth.py`
3. Check server logs for detailed error messages
4. Verify environment variables are set correctly

