from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi_app import models_fa as models
from fastapi_app.database import get_db
import os

pwd_context    = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme  = OAuth2PasswordBearer(tokenUrl='/api/auth/token')
SECRET_KEY     = os.getenv('SECRET_KEY')
ALGORITHM      = os.getenv('ALGORITHM', 'HS256')
EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 1))
REFRESH_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', 1440))  # 24 horas

def verify_password(plain, hashed):    return pwd_context.verify(plain, hashed)
def get_password_hash(password):       return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=EXPIRE_MINUTES))
    to_encode['exp'] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=REFRESH_EXPIRE_MINUTES))
    to_encode['exp'] = expire
    to_encode['type'] = 'refresh'
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme),
                    db: Session = Depends(get_db)) -> models.Usuario:
    exc = HTTPException(status_code=401, detail='Token inválido o expirado',
                        headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if not username: raise exc
    except JWTError:
        raise exc
    user = db.query(models.Usuario).filter(models.Usuario.username==username).first()
    if not user: raise exc
    return user

def get_current_user_from_refresh(token: str, db: Session) -> models.Usuario:
    exc = HTTPException(status_code=401, detail='Refresh token inválido',
                        headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'refresh':
            raise exc
        username = payload.get('sub')
        if not username: raise exc
    except JWTError:
        raise exc
    user = db.query(models.Usuario).filter(models.Usuario.username==username).first()
    if not user: raise exc
    return user

def get_current_admin(user: models.Usuario = Depends(get_current_user)) -> models.Usuario:
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='No tienes permisos de administrador')
    return user
