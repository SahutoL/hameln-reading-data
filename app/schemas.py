from pydantic import BaseModel

class LoginRequest(BaseModel):
    userId: str
    password: str