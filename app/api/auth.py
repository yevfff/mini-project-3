from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])


@router.post('/api/login', response_model=schemas.Token, status_code=status.HTTP_200_OK)
def login(
        response: Response,
        user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(database.get_db)
):
    """
    Логін користувача за допомогою email та пароля.

    - **email**: Адреса електронної пошти.
    - **password**: Пароль.

    Якщо користувач не знайдений або введені неправильні облікові дані, буде викликано помилку 403 (Forbidden).

    **Response**
    - **access_token**: Токен доступу для аутентифікації користувача.
    - **token_type**: Тип токену (наприклад, "bearer").
    """
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        path="/"
    )

    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     httponly=True,
    #     secure=False,
    #     path="/"
    # )

    return {"access_token": access_token, "token_type": "bearer"}

