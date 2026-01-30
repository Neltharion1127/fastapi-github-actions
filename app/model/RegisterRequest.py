# @Time: 1/30/26 00:36
# @Author: jie
# @File: RegisterRequest.py
# @Description:
from pydantic import BaseModel
class RegisterRequest(BaseModel):
    username: str
    password: str
