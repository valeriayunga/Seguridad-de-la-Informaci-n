import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from core.database import Sesion, Historial

# Capa de Servicio de Sesión: Gestiona el ciclo de vida de las sesiones (RS5, RS7)

def create_user_session(db_session: Session, user_id: int, sesion_id: str, ip: str):
    """RS5/RS7: Guarda la nueva sesión activa en la base de datos."""
    nueva_sesion = Sesion(
        id_sesion=sesion_id,
        id_user=user_id,
        status_sesion="ACTIVA",
        tiempo_expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        datetime=datetime.datetime.utcnow()
    )
    
    # RS3: Registrar el login exitoso (Paso 2)
    log_login_2fa = Historial(
        id_user=user_id,
        id_sesion=sesion_id,
        accion_realizada="LOGIN_EXITOSO_2FA_OK",
        ip=ip,
        id_accion=201
    )
    db_session.add(nueva_sesion)
    db_session.add(log_login_2fa)
    db_session.commit()

def expire_user_session(db_session: Session, sesion_id: str, user_id: int, ip: str):
    """RS5/RS7: Expira una sesión al hacer logout."""
    sesion = db_session.query(Sesion).filter(Sesion.id_sesion == sesion_id).first()
    if sesion:
        sesion.status_sesion = "EXPIRADA"
        
        log_logout = Historial(
            id_user=user_id,
            id_sesion=sesion_id,
            accion_realizada="LOGOUT_EXITOSO",
            ip=ip,
            id_accion=300
        )
        db_session.add(log_logout)
        db_session.commit()

def expire_all_user_sessions(db_session: Session, user_id: int, ip: str):
    """RS5: Invalida todas las sesiones antiguas de un usuario."""
    sesiones_antiguas = db_session.query(Sesion).filter(
        and_(
            Sesion.id_user == user_id,
            Sesion.status_sesion == "ACTIVA"
        )
    ).all()
    
    for sesion_vieja in sesiones_antiguas:
        sesion_vieja.status_sesion = "EXPIRADA"
        log_sesion_exp = Historial(
            id_user=user_id, 
            id_sesion=sesion_vieja.id_sesion, 
            accion_realizada="SESION_EXPIRADA_POR_NUEVO_LOGIN", 
            ip=ip, 
            id_accion=301
        )
        db_session.add(log_sesion_exp)
    # El commit se hará en la función que llame a esta