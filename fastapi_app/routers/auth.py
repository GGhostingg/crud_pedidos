from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi_app import auth, models_fa as models, schemas
from fastapi_app.database import get_db

router = APIRouter(prefix='/api/auth', tags=['Autenticación JWT'])

@router.post('/register')
def registrar(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(
        (models.Usuario.username == datos.username) | (models.Usuario.email == datos.email)
    ).first():
        raise HTTPException(400, 'Usuario o email ya existe')
    nuevo = models.Usuario(
        username=datos.username,
        email=datos.email,
        hashed_password=auth.get_password_hash(datos.password),
        is_staff=datos.is_staff,
    )
    db.add(nuevo); db.commit(); db.refresh(nuevo)
    return {'mensaje': 'Usuario creado', 'username': nuevo.username}

@router.post('/token', response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(
        models.Usuario.username == form.username
    ).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(401, 'Credenciales incorrectas',
                            headers={'WWW-Authenticate': 'Bearer'})
    access_token = auth.create_access_token(
        {'sub': user.username},
        timedelta(minutes=auth.EXPIRE_MINUTES)
    )
    refresh_token = auth.create_refresh_token({'sub': user.username})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.post('/refresh', response_model=schemas.Token)
def refresh_token(request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    user = auth.get_current_user_from_refresh(request.refresh_token, db)
    access_token = auth.create_access_token(
        {'sub': user.username},
        timedelta(minutes=auth.EXPIRE_MINUTES)
    )
    refresh_token = auth.create_refresh_token({'sub': user.username})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}
