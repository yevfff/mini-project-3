import jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_access_token(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return token

    token = request.headers.get("Authorization")
    if token:
        return token

    raise HTTPException(status_code=401, detail="Token missing or invalid")

def get_access_token_for_websocket(websocket: WebSocket):
    token = websocket.cookies.get("access_token")
    if token:
        return token

    token = websocket.headers.get("Authorization")
    if token:
        return token
    raise HTTPException(status_code=401, detail="Token missing or invalid")


def verify_access_token(token: str, credentials_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except jwt.PyJWKError:
        raise credentials_exception

    return token_data


# def get_current_user(#token: str = Depends(oauth2_scheme)
#                     token: str = Depends(get_access_token_from_cookie), db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                           detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

#     token = verify_access_token(token, credentials_exception)

#     user = db.query(models.User).filter(models.User.id == token.id).first()

#     return user


def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = get_access_token(request) 
    token_data = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    if not user:
        raise credentials_exception

    return user



async def get_user_from_token(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    if not user:
        raise credentials_exception

    return user


# def get_token_from_cookies(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         token = request.headers.get("Authorization")
#     if not token:
#         raise HTTPException(
#             status_code=401,
#             detail="Access token is missing from cookies",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     return token

