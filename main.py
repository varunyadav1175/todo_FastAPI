from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional
from typing import Optional
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Item(BaseModel):
    title: str
    description: str
    done: Optional[bool] = False

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import timedelta

# Initialize FastAPI app
app = FastAPI()

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    password: str

# Item model
class Item(BaseModel):
    name: str
    done: bool = False

# Access token expire time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_db():
    """
    Connect to MongoDB and return the database instance.
    """
    client = AsyncIOMotorClient('mongodb+srv://varunyadav1175:Bhapy5548p@todos.1lnj7dw.mongodb.net')
    return client.todo_list

async def authenticate_user(fake_db, username: str, password: str):
    """
    Authenticate a user against the provided database.

    Args:
        fake_db: The database to authenticate against.
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        The user if authentication is successful, False otherwise.
    """
    user = await fake_db["users"].find_one({"username": username})
    if not user:
        return False
    if not pwd_context.verify(password, user["password"]):
        return False
    return user

@app.post("/signup")
async def signup(user: User, db=Depends(get_db)):
    """
    Sign up a new user.

    Args:
        user (User): The user to sign up.
        db: The database to add the user to.

    Returns:
        A message indicating the user was created successfully.
    """
    hashed_password = pwd_context.hash(user.password)
    new_user = {"username": user.username, "password": hashed_password}
    if await db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    await db["users"].insert_one(new_user)
    return {"message": "User created successfully"}

@app.post("/token")
async def login(form_data: User, db=Depends(get_db)):
    """
    Log in a user.

    Args:
        form_data (User): The login form data.
        db: The database to authenticate against.

    Returns:
        A token if login is successful, raises an HTTPException otherwise.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/todos/")
async def read_all_todos(db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Get all todos.

    Args:
        db: The database to get todos from.
        token (str): The user's token.

    Returns:
        A list of all todos.
    """
    todos = []
    for todo in await db["todos"].find().to_list(length=100):
        todo["_id"] = str(todo["_id"])  # Convert ObjectId to string
        todos.append(todo)
    return todos

@app.post("/todos/")
async def create_todo(todo: Item, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Create a new todo.

    Args:
        todo (Item): The todo to create.
        db: The database to add the todo to.
        token (str): The user's token.

    Returns:
        The id of the created todo.
    """
    todo = await db["todos"].insert_one(todo.dict())
    return {"id": str(todo.inserted_id)}

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: str, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Update a todo.

    Args:
        todo_id (str): The id of the todo to update.
        db: The database to update the todo in.
        token (str): The user's token.

    Returns:
        The updated todo, raises an HTTPException if the todo is not found.
    """
    response = await db["todos"].update_one({"_id": ObjectId(todo_id)}, {"$set": {"done": True}})
    if response.matched_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated_todo = await db["todos"].find_one({"_id": ObjectId(todo_id)})
    updated_todo["_id"] = str(updated_todo["_id"])  # Convert ObjectId to string
    return updated_todo

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Delete a todo.

    Args:
        todo_id (str): The id of the todo to delete.
        db: The database to delete the todo from.
        token (str): The user's token.

    Returns:
        The number of todos deleted, raises an HTTPException if the todo is not found.
    """
    response = await db["todos"].delete_one({"_id": ObjectId(todo_id)})
    if response.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"deleted_count": response.deleted_count}