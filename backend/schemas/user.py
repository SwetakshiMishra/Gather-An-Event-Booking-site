from pydantic import BaseModel, EmailStr,Field

class User_register(BaseModel):
    email: EmailStr
    name: str
    password: str
    age: int | None = None
    college:str
    course:str
    graduation_year:int= Field(ge=3)


class User_login(BaseModel):
    email: EmailStr
    password: str



class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    age: int | None
    college: str
    course: str
    graduation_year: int

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    refresh_token: str