import bcrypt

# Capa de Seguridad: Solo se encarga de hashear y verificar.

def hash_password(password: str) -> str:
    """Hashea la contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verifica la contraseña contra el hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))