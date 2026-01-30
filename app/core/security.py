# @Time: 1/29/26 19:14
# @Author: jie
# @File: security.py
# @Description:
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return pwd_context.verify(password, password_hash)