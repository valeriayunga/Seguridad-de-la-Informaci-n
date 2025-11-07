from sqlalchemy.orm import Session
from core.database import Cliente, Credenciales, Historial, Sesion

# Capa de Servicio de Admin: Funciones para el panel de admin (RS3, RS5)

def get_full_history(db_session: Session):
    """RS3: Obtiene todos los registros de la tabla Historial."""
    history = db_session.query(
        Historial.datetime,
        Historial.accion_realizada,
        Historial.ip,
        Credenciales.usuario.label("usuario"),
        Sesion.id_sesion
    ).outerjoin(
        Credenciales, Historial.id_user == Credenciales.id_user
    ).outerjoin(
        Sesion, Historial.id_sesion == Historial.id_sesion
    ).order_by(
        Historial.datetime.desc()
    ).all()
    
    return history

def get_all_users_for_admin(db_session: Session):
    """RS5: Obtiene todos los usuarios para el panel de admin."""
    users = db_session.query(
        Cliente.id_user,
        Cliente.nombres,
        Cliente.apellidos,
        Cliente.mail,
        Credenciales.usuario,
        Credenciales.rol,
        Credenciales.activo,
        Credenciales.bloqueo
    ).join(
        Credenciales, Cliente.id_user == Credenciales.id_user
    ).all()
    
    return users

def toggle_user_active_status(db_session: Session, user_id: int) -> bool:
    """RS5: Cambia el estado 'activo' (baja temporal) de un usuario."""
    credencial = db_session.query(Credenciales).filter(Credenciales.id_user == user_id).first()
    if credencial:
        credencial.activo = not credencial.activo
        db_session.commit()
        return credencial.activo
    return False