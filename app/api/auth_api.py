from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.database.session import get_db
from app.models.user import UserModel
from app.schemas.response import TokenResponseSchema
from app.schemas.request import UserLoginRequestSchema
from app.auth.jwt_auth import create_access_token


router = APIRouter(prefix="/auth",tags=["Authentication"])

password_hash = PasswordHash.recommended()


@router.post("/login",response_model=TokenResponseSchema)
def login(request: UserLoginRequestSchema,db: Session = Depends(get_db)):
    user = (
        db.query(UserModel)
        .filter(UserModel.username == request.username)
        .first()
    )

    if user is None or not password_hash.verify(request.password , user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive.",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }