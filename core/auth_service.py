import random
import string
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.database import Cliente, Credenciales, Historial
from core.security import hash_password, check_password
from core.session_service import expire_all_user_sessions
from core.token_service import verify_reset_token

# Capa de Servicio de Autenticación: Lógica principal de negocio

def create_user(db_session: Session, cedula: str, nombres: str, apellidos: str, mail: str, telefono: str, ip: str):
    """RS1: El sistema genera usuario y contraseña."""
    try:
        usuario_generado = (nombres[0] + apellidos.split(' ')[0]).lower()
        password_plano = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_pass = hash_password(password_plano)
        
        nuevo_cliente = Cliente(
            cedula=cedula, nombres=nombres, apellidos=apellidos,
            mail=mail, telefono=telefono
        )
        
        nuevas_credenciales = Credenciales(
            usuario=usuario_generado,
            contrasena_hash=hashed_pass,
            cliente=nuevo_cliente,
            rol="ADMIN" if db_session.query(Cliente).count() == 0 else "USUARIO"
        )
        
        db_session.add(nuevo_cliente)
        db_session.add(nuevas_credenciales)
        db_session.commit()
        
        # RS3: Registrar la creación en el Historial
        log_creacion = Historial(
            id_user=nuevo_cliente.id_user,
            accion_realizada="USUARIO_CREADO",
            ip=ip,
            id_accion=100
        )
        db_session.add(log_creacion)
        db_session.commit()
        
        return True, (usuario_generado, password_plano), nuevo_cliente.id_user

    except IntegrityError:
        db_session.rollback()
        return False, "Error: El email, cédula o teléfono ya existe.", None
    except Exception as e:
        db_session.rollback()
        return False, f"Ocurrió un error inesperado: {e}", None

def activate_account(db_session: Session, usuario: str, codigo: str) -> (bool, str):
    """RS1: Intenta activar una cuenta usando el código de 6 dígitos."""
    from core.token_service import verify_2fa_token # Import local
    
    credencial = db_session.query(Credenciales).filter(Credenciales.usuario == usuario).first()
    
    if not credencial:
        return False, "Usuario no encontrado"
        
    if credencial.validado:
        return False, "Esta cuenta ya ha sido activada."
    
    # Reutilizamos la lógica de verify_2fa_token pero con tipo "ACTIVACION"
    # (¡Podríamos refactorizar token_service para tener una función genérica!)
    from core.database import TokenValidacion
    from sqlalchemy import and_
    import datetime

    token = db_session.query(TokenValidacion).filter(
        and_(
            TokenValidacion.id_user == credencial.id_user,
            TokenValidacion.token_type == "ACTIVACION",
            TokenValidacion.usado == False,
            TokenValidacion.expiracion > datetime.datetime.utcnow()
        )
    ).first()
    
    if not token:
        return False, "Código incorrecto, expirado o no encontrado."
        
    if check_password(codigo, token.token_hast):
        credencial.validado = True
        token.usado = True
        db_session.commit()
        return True, "¡Cuenta activada! Ya puedes iniciar sesión."
    else:
        return False, "Código incorrecto."

def verify_login_attempt(db_session: Session, usuario: str, password: str, ip: str):
    """Verifica las credenciales de un usuario."""
    credencial = db_session.query(Credenciales).filter(Credenciales.usuario == usuario).first()
    
    if not credencial:
        log_fallido = Historial(id_user=None, accion_realizada="LOGIN_FALLIDO_USUARIO_INEXISTENTE", ip=ip, id_accion=101)
        db_session.add(log_fallido)
        db_session.commit()
        return "ERROR", "Usuario o contraseña incorrectos"

    user_id = credencial.id_user

    if credencial.bloqueo:
        log_bloqueado = Historial(id_user=user_id, accion_realizada="LOGIN_FALLIDO_CUENTA_BLOQUEADA", ip=ip, id_accion=102)
        db_session.add(log_bloqueado)
        db_session.commit()
        return "ERROR", "Cuenta bloqueada por demasiados intentos."

    if not credencial.activo:
        log_inactivo = Historial(id_user=user_id, accion_realizada="LOGIN_FALLIDO_CUENTA_INACTIVA", ip=ip, id_accion=105)
        db_session.add(log_inactivo)
        db_session.commit()
        return "ERROR", "Esta cuenta ha sido dada de baja temporalmente."

    password_ok = check_password(password, credencial.contrasena_hash)
    
    if not password_ok:
        credencial.intentos_restantes -= 1
        log_accion = "LOGIN_FALLIDO_CONTRASENA_INCORRECTA"
        if credencial.intentos_restantes <= 0:
            credencial.bloqueo = True
            log_accion = "CUENTA_BLOQUEADA_POR_INTENTOS"
        log_fallo_pass = Historial(id_user=user_id, accion_realizada=log_accion, ip=ip, id_accion=103)
        db_session.add(log_fallo_pass)
        db_session.commit()
        return "ERROR", "Usuario o contraseña incorrectos"

    # Contraseña CORRECTA
    credencial.intentos_restantes = 4
    
    if not credencial.validado:
        log_no_validado = Historial(id_user=user_id, accion_realizada="LOGIN_FALLIDO_CUENTA_NO_ACTIVADA", ip=ip, id_accion=104)
        db_session.add(log_no_validado)
        db_session.commit()
        return "ERROR", "Tu cuenta aún no ha sido activada. Ve a la pestaña 'Activar Cuenta'."

    # RS5 (Sesiones simultáneas)
    expire_all_user_sessions(db_session, user_id, ip)
        
    log_exito_pass = Historial(id_user=user_id, accion_realizada="LOGIN_EXITOSO_PASSWORD_OK", ip=ip, id_accion=200)
    db_session.add(log_exito_pass)
    db_session.commit()
    
    return "REQUIERE_2FA", user_id

def reset_password_with_token(db_session: Session, email: str, token_plano: str, nueva_password: str) -> (bool, str):
    """Verifica el token de reseteo y actualiza la contraseña (RS4)."""
    
    cliente = db_session.query(Cliente).filter(Cliente.mail == email).first()
    if not cliente:
        return False, "Email o token incorrecto."

    # Verificar el token
    success_token, msg_token, token_obj = verify_reset_token(db_session, cliente.id_user, token_plano)
    
    if not success_token:
        return False, msg_token

    # Token es válido, proceder a cambiar la contraseña
    credencial = db_session.query(Credenciales).filter(Credenciales.id_user == cliente.id_user).first()
    if not credencial:
        return False, "Error: El usuario no tiene credenciales asociadas."
        
    credencial.contrasena_hash = hash_password(nueva_password)
    token_obj.usado = True # Marcar el token como usado
    credencial.bloqueo = False
    credencial.intentos_restantes = 4
    
    db_session.commit()
    return True, "¡Contraseña actualizada exitosamente! Ya puedes iniciar sesión."