from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str):
    return pwd_context.hash(password)

# Пример использования:
plain_password = "lera2004"
hashed_password = hash_password(plain_password)
print("Hashed password:", hashed_password)