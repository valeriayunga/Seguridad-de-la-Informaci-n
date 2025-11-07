import datetime
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
DATABASE_URL = "sqlite:///auth_practica.db"
engine = db.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. MODELOS DE TABLAS (Corregidos) ---

class Cliente(Base):
    __tablename__ = 'cliente'
    id_user = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String, unique=True, nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    telefono = Column(String, unique=True, nullable=False)
    
    credenciales = relationship("Credenciales", back_populates="cliente", uselist=False)
    tokens = relationship("TokenValidacion", back_populates="cliente")
    autenticadores = relationship("Authentication", back_populates="cliente")
    historial = relationship("Historial", back_populates="cliente")
    # RS5: Relación con Sesiones
    sesiones = relationship("Sesion", back_populates="cliente")

class Credenciales(Base):
    __tablename__ = 'credenciales'
    id_user = Column(Integer, ForeignKey('cliente.id_user'), primary_key=True)
    usuario = Column(String, unique=True, nullable=False)
    contrasena_hash = Column(String, nullable=False)
    datetime_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    validado = Column(Boolean, default=False)
    activo = Column(Boolean, default=True) # Para RS5 (Baja temporal)
    cantidad_sesiones = Column(Integer, default=0)
    bloqueo = Column(Boolean, default=False)
    intentos_restantes = Column(Integer, default=4)
    # RS3: Para saber quién es Admin
    rol = Column(String, default="USUARIO") # "USUARIO" o "ADMIN"
    
    cliente = relationship("Cliente", back_populates="credenciales")

class TokenValidacion(Base):
    __tablename__ = 'token_validacion'
    id_token = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('cliente.id_user'), nullable=False)
    token_hast = Column(String, unique=True, nullable=False)
    token_type = Column(String, nullable=False) # "ACTIVACION", "RESETEO", "LOGIN_2FA"
    expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)
    
    cliente = relationship("Cliente", back_populates="tokens")


class Authentication(Base):
    __tablename__ = 'authentication'
    id_autenticador = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('cliente.id_user'), nullable=False)
    id_credencial_webauthn = Column(String, unique=True)
    public_key_base64 = Column(String)
    nombre_dispositivo = Column(String)
    tipo = Column(String)
    
    cliente = relationship("Cliente", back_populates="autenticadores")
    historial = relationship("Historial", back_populates="autenticador")


class Sesion(Base):
    __tablename__ = 'sesion'
    id_sesion = Column(String, primary_key=True)
    # RS5: Añadimos id_user para saber de quién es la sesión
    id_user = Column(Integer, ForeignKey('cliente.id_user'), nullable=False)
    status_sesion = Column(String) # "ACTIVA", "PENDIENTE_2FA", "EXPIRADA"
    tiempo_expiracion = Column(DateTime)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    
    # RS5: Relación con Cliente
    cliente = relationship("Cliente", back_populates="sesiones")
    
    # Fix para el error de 'sesion'
    historial_rel = relationship("Historial", back_populates="sesion_rel")


class Historial(Base):
    __tablename__ = 'historial'
    id_historial = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('cliente.id_user'), nullable=True)
    id_sesion = Column(String, ForeignKey('sesion.id_sesion'), nullable=True)
    id_autenticador = Column(Integer, ForeignKey('authentication.id_autenticador'), nullable=True)
    id_accion = Column(Integer)
    accion_realizada = Column(String, nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    ip = Column(String, nullable=True)
    
    cliente = relationship("Cliente", back_populates="historial")
    autenticador = relationship("Authentication", back_populates="historial")
    # Fix para el error de 'sesion'
    sesion_rel = relationship("Sesion", back_populates="historial_rel")


# --- 3. FUNCIONES DE CONEXIÓN ---

def get_db():
    """Generador de sesión de base de datos."""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

def create_db_tables():
    """Crea todas las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)