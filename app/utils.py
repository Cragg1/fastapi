from passlib.context import CryptContext

# Telling passlib to use bcrypt as the default hashing algorithm. Used for hashing passwords in the database.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(secret=plain_password, hash=hashed_password)
