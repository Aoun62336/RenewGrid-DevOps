"""
core/deps.py — Reusable FastAPI dependencies.

Import `get_current_user` in any route that requires authentication.
Import `require_role(...)` to restrict a route to one or more roles.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service

# OAuth2 bearer token extractor — reads the Authorization: Bearer <token> header
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: decode the JWT from the Authorization header and return
    the active User object.  Raises 401 on any auth failure.
    """
    return auth_service.get_current_user(db, token=credentials.credentials)


def require_role(*allowed_roles: UserRole):
    """
    Factory dependency: restricts route access to the specified roles.

    Usage in a route:
        @router.get("/admin-only")
        def admin_route(user = Depends(require_role(UserRole.ADMIN))):
            ...
    """

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: "
                       f"{[r.value for r in allowed_roles]}",
            )
        return current_user

    return _check

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency: ensure the current user is an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
