from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .settings import settings

# Configure bcrypt with explicit rounds to ensure compatibility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def _bcrypt_safe(pw: str) -> str:
    """
    bcrypt only uses the first 72 BYTES of the password.
    Truncate safely at character boundaries.
    """
    if pw is None:
        raise ValueError("password is None")
    
    # Convert to string and encode
    pw = str(pw)
    encoded = pw.encode("utf-8")
    
    # If within limit, return as-is
    if len(encoded) <= 72:
        return pw
    
    # Truncate at a safe character boundary
    # Work backwards from byte 72 to find valid UTF-8 boundary
    for length in range(72, 0, -1):
        try:
            return encoded[:length].decode("utf-8")
        except UnicodeDecodeError:
            continue
    
    # Fallback: return first 72 ASCII characters if all else fails
    return pw[:72]

def hash_password(pw: str) -> str:
    """Hash a password safely with bcrypt."""
    if not pw:
        raise ValueError("password cannot be empty")
    
    # Ensure password is within bcrypt limits
    safe_pw = _bcrypt_safe(pw)
    
    # Double-check the byte length after processing
    if len(safe_pw.encode("utf-8")) > 72:
        # Force truncate if still too long
        safe_pw = safe_pw.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    
    return pwd_context.hash(safe_pw)

def verify_password(pw: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    try:
        pw = _bcrypt_safe(pw)
    except Exception:
        return False
    return pwd_context.verify(pw, hashed)

def create_access_token(sub: str, role: str, school_id: Optional[str] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {"sub": sub, "role": role, "school_id": school_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_user(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_token(token)