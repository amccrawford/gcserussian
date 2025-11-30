import bcrypt

def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

# Note: verify_password is removed for now due to passlib compatibility issues.
# If full passlib functionality is required, this issue needs further investigation.
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
