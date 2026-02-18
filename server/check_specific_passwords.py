
from server.database import SessionLocal
from server import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
db = SessionLocal()
users = db.query(models.User).limit(3).all()

print("Checking first 3 users for password 'password123'...")
for u in users:
    is_match = pwd_context.verify("password123", u.hashed_password)
    status = "MATCHES" if is_match else "DOES NOT MATCH"
    print(f"User: {u.email} (ID: {u.id}) - {status}")
