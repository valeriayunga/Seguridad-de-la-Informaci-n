import datetime
import random
import string
from typing import Optional # <-- CAMBIO 1: Importar Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from core.database import TokenValidacion
from core.security import hash_password, check_password # Importa de nuestro módulo

# Capa de Servicio de Tokens: Gestiona solo la creación y validación de tokens

def generate_activation_token(db_session: Session, user_id: int) -> str:
    """Genera un token de 6 dígitos para ACTIVACION (RS1)."""
    token_plano = ''.join(random.choices(string.digits, k=6))
    token_hash = hash_password(token_plano) 
    
    nuevo_token = TokenValidacion(
        id_user=user_id,
        token_hast=token_hash,
        token_type="ACTIVACION",
        expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        usado=False
    )
    db_session.add(nuevo_token)
    db_session.commit()
    return token_plano

def generate_2fa_token(db_session: Session, user_id: int) -> str:
    """Genera un token de 6 dígitos para LOGIN (RS2)."""
    token_plano = ''.join(random.choices(string.digits, k=6))
    token_hash = hash_password(token_plano)
    
    nuevo_token = TokenValidacion(
        id_user=user_id,
        token_hast=token_hash,
        token_type="LOGIN_2FA",
        expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        usado=False
    )
    db_session.add(nuevo_token)
    db_session.commit()
    return token_plano

def verify_2fa_token(db_session: Session, user_id: int, codigo: str) -> (bool, str):
    """Verifica el código de 6 dígitos del login (RS2)."""
    token = db_session.query(TokenValidacion).filter(
        and_(
            TokenValidacion.id_user == user_id,
            TokenValidacion.token_type == "LOGIN_2FA",
            TokenValidacion.usado == False,
            TokenValidacion.expiracion > datetime.datetime.utcnow()
        )
    ).order_by(TokenValidacion.id_token.desc()).first()
    
    if not token:
        return False, "Código incorrecto, expirado o no encontrado."
        
    if check_password(codigo, token.token_hast):
        token.usado = True
        db_session.commit()
        return True, "Código 2FA correcto."
    else:
        return False, "Código incorrecto."

def generate_reset_token(db_session: Session, email: str) -> (bool, str, Optional[int]): # <-- CAMBIO 2
    """
    Busca un usuario por email y genera un token de reseteo (RS4).
    Devuelve (True, token_plano, user_id) o (False, "mensaje de error", None).
    """
    # Necesitamos importar Cliente aquí para evitar importación circular
    from core.database import Cliente
    cliente = db_session.query(Cliente).filter(Cliente.mail == email).first()
    
    if not cliente:
        return False, "Si este email está registrado, se enviará un código.", None

    token_plano = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    token_hash = hash_password(token_plano)
    
    nuevo_token = TokenValidacion(
        id_user=cliente.id_user,
        token_hast=token_hash,
        token_type="RESETEO",
        expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        usado=False
    )
    db_session.add(nuevo_token)
    db_session.commit()
    
    return True, token_plano, cliente.id_user

def verify_reset_token(db_session: Session, user_id: int, token_plano: str) -> (bool, str, Optional[TokenValidacion]): # <-- CAMBIO 3
    """Verifica que un token de reseteo sea válido."""
    token = db_session.query(TokenValidacion).filter(
        and_(
            TokenValidacion.id_user == user_id,
            TokenValidacion.token_type == "RESETEO",
            TokenValidacion.usado == False,
            TokenValidacion.expiracion > datetime.datetime.utcnow()
        )
    ).order_by(TokenValidacion.id_token.desc()).first()
    
    if not token:
        return False, "Token incorrecto, expirado o no encontrado.", None
    
    if check_password(token_plano, token.token_hast):
        return True, "Token verificado.", token
    else:
        return False, "Token incorrecto.", None
