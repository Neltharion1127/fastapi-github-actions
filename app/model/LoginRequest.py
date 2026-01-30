# @Time: 1/28/26 03:22
# @Author: jie
# @File: LoginRequest.py
# @Description:
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str