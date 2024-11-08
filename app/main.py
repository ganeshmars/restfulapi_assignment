import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud, database, auth
from .database import get_db, Base, engine
from fastapi.security import OAuth2PasswordRequestForm
from .auth import authenticate_user, create_access_token, get_password_hash
from datetime import timedelta
from .auth import get_current_user

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

SECRET_KEY = 'efc75531ddbdcc0c45304a720e1e4efb6c74ff1ef9381efaf15e4bfe4950b205'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_username = crud.get_user_by_username(db, user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_by_email = crud.get_user_by_email(db, user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.UserOut])
def read_users(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.User)
    if search:
        query = query.filter(
            (models.User.username.contains(search)) | (models.User.email.contains(search))
        )
    users = query.offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(get_current_user)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Endpoint to update user details by ID
@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(get_current_user)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    return updated_user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}