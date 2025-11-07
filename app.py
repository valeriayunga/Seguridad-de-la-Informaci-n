import streamlit as st
from streamlit_option_menu import option_menu
import uuid # Para generar IDs de sesión únicos

# Importamos las funciones de los otros archivos
# ¡Nota cómo las importaciones ahora vienen de la carpeta 'core' y están organizadas!
from core.database import create_db_tables, get_db, Cliente, Credenciales
from core.auth_service import (
    create_user,
    activate_account,
    verify_login_attempt,
    reset_password_with_token
)
from core.token_service import (
    generate_activation_token,
    generate_2fa_token,
    verify_2fa_token,
    generate_reset_token
)
from core.admin_service import (
    get_full_history,
    get_all_users_for_admin,
    toggle_user_active_status
)
from core.session_service import (
    create_user_session,
    expire_user_session
)


# --- 1. CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(page_title="Práctica de Autenticación", layout="centered")

# --- 2. GESTIÓN DE ESTADO DE LA SESIÓN ---
if "login_step" not in st.session_state:
    st.session_state.login_step = "PASSWORD"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "usuario_login" not in st.session_state:
    st.session_state.usuario_login = ""
if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = None
if "admin_page_selector" not in st.session_state:
    st.session_state.admin_page_selector = "Ninguna"
if "reset_step" not in st.session_state:
    st.session_state.reset_step = "REQUEST"
if "reset_token" not in st.session_state:
    st.session_state.reset_token = None


# --- 3. INTERFAZ GRÁFICA (Streamlit) ---
def main():
    create_db_tables()
    db_session = next(get_db())
    ip_simulada = "127.0.0.1" # Definimos la IP simulada para toda la app

    # --- BARRA LATERAL (Solo Controles) ---
    with st.sidebar:
        selected = option_menu(
            "Menú Principal", 
            ["Login", "Registro", "Activar Cuenta", "Recuperar Contraseña"],
            icons=['box-arrow-in-right', 'person-plus-fill', 'check-circle-fill', 'key-fill'], 
            menu_icon="cast", 
            default_index=0
        )
        
        # RS3/RS5: Panel de Admin (CONTROLES)
        if st.session_state.login_step == "LOGGED_IN":
            user_rol_query = db_session.query(Credenciales).filter(Credenciales.id_user == st.session_state.user_id).first()
            if user_rol_query and user_rol_query.rol == "ADMIN":
                st.sidebar.title("---")
                st.sidebar.header("Panel de Administrador")
                st.sidebar.radio(
                    "Opciones de Admin",
                    ["Ninguna", "Ver Historial (RS3)", "Gestionar Usuarios (RS5)"],
                    key="admin_page_selector"
                )
                st.sidebar.title("---")

    
    # --- PANTALLA PRINCIPAL ---

    # --- PÁGINA DE LOGIN ---
    if selected == "Login":

        # --- ESTADO 1: Pedir Usuario/Contraseña ---
        if st.session_state.login_step == "PASSWORD":
            st.title("🔐 Login de Usuario")
            with st.form("login_form"):
                usuario = st.text_input("Usuario", key="login_usuario")
                password = st.text_input("Contraseña", type="password", key="login_password")
                submitted = st.form_submit_button("Ingresar")

                if submitted:
                    if not usuario or not password:
                        st.error("Por favor, ingresa usuario y contraseña.")
                    else:
                        status, message_or_id = verify_login_attempt(db_session, usuario, password, ip_simulada)
                        
                        if status == "ERROR":
                            st.error(message_or_id)
                        elif status == "REQUIERE_2FA":
                            st.session_state.user_id = message_or_id
                            st.session_state.usuario_login = usuario
                            codigo_2fa = generate_2fa_token(db_session, message_or_id)
                            st.info("Contraseña correcta. Simulación de 2FA (RS2):")
                            st.code(f"Tu código de login (2FA) es: {codigo_2fa}")
                            st.session_state.login_step = "2FA_PENDING_DISPLAY"

        # --- ESTADO 2: Pedir Código 2FA ---
        elif st.session_state.login_step == "2FA_PENDING_DISPLAY":
            st.title("🔒 Verificación de 2 Pasos (RS2)")
            st.info(f"¡Hola, {st.session_state.usuario_login}! Ingresa el código 2FA que te mostramos.")
            
            with st.form("2fa_form"):
                codigo = st.text_input("Ingresa el código de 6 dígitos")
                submitted_2fa = st.form_submit_button("Verificar Código")

                if submitted_2fa:
                    success, message = verify_2fa_token(db_session, st.session_state.user_id, codigo)
                    
                    if success:
                        st.success("¡Login exitoso!")
                        st.session_state.login_step = "LOGGED_IN"
                        sesion_id_unica = str(uuid.uuid4())
                        st.session_state.sesion_id = sesion_id_unica
                        
                        # Llamamos al servicio de sesión
                        create_user_session(
                            db_session, 
                            st.session_state.user_id, 
                            sesion_id_unica, 
                            ip_simulada
                        )
                        
                        st.rerun()
                    else:
                        st.error(message)

        # --- ESTADO 3: Sesión Iniciada ---
        elif st.session_state.login_step == "LOGGED_IN":
            st.title(f"🎉 ¡Bienvenido, {st.session_state.usuario_login}!")
            st.success("Has iniciado sesión correctamente.")
            st.info(f"ID de Sesión (RS5): {st.session_state.sesion_id}")
            
            if st.button("Cerrar Sesión (Logout)"):
                expire_user_session(
                    db_session, 
                    st.session_state.sesion_id, 
                    st.session_state.user_id, 
                    ip_simulada
                )
                
                # Limpiar estados de Streamlit
                st.session_state.login_step = "PASSWORD"
                st.session_state.user_id = None
                st.session_state.usuario_login = ""
                st.session_state.sesion_id = None
                st.session_state.admin_page_selector = "Ninguna"
                st.rerun()

            # --- Panel de Admin (CONTENIDO EN PANTALLA PRINCIPAL) ---
            user_rol_query = db_session.query(Credenciales).filter(Credenciales.id_user == st.session_state.user_id).first()
            if user_rol_query and user_rol_query.rol == "ADMIN":
                
                admin_page_choice = st.session_state.admin_page_selector
                
                if admin_page_choice == "Ver Historial (RS3)":
                    st.divider()
                    st.header("👁️ Visor del Historial (RS3)")
                    st.info("Monitoreo de todas las acciones del sistema.")
                    history_data = get_full_history(db_session)
                    if history_data:
                        st.dataframe(history_data, use_container_width=True)
                    else:
                        st.warning("No hay registros en el historial.")

                elif admin_page_choice == "Gestionar Usuarios (RS5)":
                    st.divider()
                    st.header("👥 Gestión de Usuarios (RS5)")
                    st.info("Dar de baja temporal (desactivar) o reactivar usuarios.")
                    all_users = get_all_users_for_admin(db_session)
                    
                    if all_users:
                        st.dataframe(all_users, use_container_width=True)
                        st.subheader("Modificar Estado (RS5)")
                        with st.form("admin_user_form"):
                            user_options = [f"{user.usuario} (ID: {user.id_user})" for user in all_users]
                            selected_user_str = st.selectbox("Selecciona un usuario", user_options)
                            submitted = st.form_submit_button("Activar / Desactivar Usuario")
                            
                            if submitted:
                                user_id_to_toggle = int(selected_user_str.split(" (ID: ")[1].replace(")", ""))
                                nuevo_estado = toggle_user_active_status(db_session, user_id_to_toggle)
                                st.success(f"¡Hecho! El usuario ahora está {'Activo' if nuevo_estado else 'Inactivo'}.")
                                st.info("Recargando la lista...")
                                st.rerun()
                    else:
                        st.warning("No hay usuarios registrados (además de ti).")

    # --- PÁGINA DE REGISTRO (RS1 - Corregida) ---
    if selected == "Registro":
        st.title("✍️ Solicitud de Registro (RS1)")
        st.info("Ingresa tus datos. El sistema te generará un usuario y contraseña.")
        
        with st.form("registro_form"):
            st.subheader("Datos Personales (Cliente)")
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            cedula = st.text_input("Cédula/Identificación")
            mail = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            
            submitted = st.form_submit_button("Solicitar Registro")

            if submitted:
                if not all([nombres, apellidos, cedula, mail, telefono]):
                    st.error("Por favor, llena todos los campos.")
                else:
                    success, data, new_user_id = create_user(
                        db_session, cedula, nombres, apellidos, 
                        mail, telefono, ip_simulada
                    )
                    
                    if success:
                        usuario_gen, pass_gen = data
                        st.success("¡Solicitud de registro exitosa!")
                        st.info("Simulación de Email (RS1):")
                        st.code(f"""
                        Tus credenciales generadas son:
                        Usuario: {usuario_gen}
                        Contraseña: {pass_gen}
                        """)
                        
                        if new_user_id:
                            codigo_activacion = generate_activation_token(db_session, new_user_id)
                            st.code(f"Tu código de activación es: {codigo_activacion}")
                        
                        st.warning("¡Guarda estos datos! Ahora ve a 'Activar Cuenta'.")
                    else:
                        st.error(data)

    # --- PÁGINA DE ACTIVAR CUENTA (RS1 - Implementada) ---
    if selected == "Activar Cuenta":
        st.title("✅ Activar Cuenta (RS1)")
        st.info("Ingresa el código de 6 dígitos que (simulamos) enviamos a tu email.")
        
        with st.form("activar_form"):
            usuario = st.text_input("Tu nombre de Usuario")
            codigo = st.text_input("Código de 6 dígitos")
            submitted = st.form_submit_button("Activar")
            
            if submitted:
                if not usuario or not codigo:
                    st.error("Por favor, llena todos los campos.")
                else:
                    success, message = activate_account(db_session, usuario, codigo)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    # --- PÁGINA DE RECUPERAR CONTRASEÑA (RS4 - Implementada) ---
    if selected == "Recuperar Contraseña":
        st.title("🔑 Recuperar Contraseña (RS4)")

        # --- PASO 1: Pedir el Email ---
        if st.session_state.reset_step == "REQUEST":
            st.info("Ingresa tu email. Te enviaremos (simularemos) un token de reseteo.")
            with st.form("request_reset_form"):
                email = st.text_input("Tu Email registrado")
                submitted = st.form_submit_button("Solicitar Token")
                if submitted:
                    if not email:
                        st.error("Por favor, ingresa un email.")
                    else:
                        success, token_or_message, user_id = generate_reset_token(db_session, email)
                        if success:
                            st.session_state.reset_token = token_or_message
                            # Guardamos el email para el siguiente paso
                            st.session_state.reset_email = email 
                            st.session_state.reset_step = "SUBMIT"
                            st.rerun()
                        else:
                            st.success(token_or_message)

        # --- PASO 2: Usar el Token ---
        elif st.session_state.reset_step == "SUBMIT":
            st.info("Ingresa el token que te enviamos y tu nueva contraseña.")
            if st.session_state.reset_token:
                st.info("Simulación de Email (RS4) - Token generado:")
                st.code(st.session_state.reset_token)
                st.warning("Copia este token y pégalo en el campo de abajo.")
            
            with st.form("submit_reset_form"):
                # Usamos el email guardado para que el usuario no tenga que escribirlo
                email_guardado = st.session_state.get("reset_email", "")
                st.text_input("Tu Email", value=email_guardado, disabled=True)
                token = st.text_input("Token de Reseteo")
                nueva_password = st.text_input("Tu Nueva Contraseña", type="password")
                
                submitted = st.form_submit_button("Cambiar Contraseña")
                
                if submitted:
                    if not all([email_guardado, token, nueva_password]):
                        st.error("Por favor, llena todos los campos.")
                    else:
                        success, message = reset_password_with_token(
                            db_session, email_guardado, token, nueva_password
                        )
                        if success:
                            st.success(message)
                            st.session_state.reset_step = "REQUEST"
                            st.session_state.reset_token = None
                            st.session_state.reset_email = None
                            st.rerun()
                        else:
                            st.error(message)

            if st.button("Cancelar y volver a solicitar token"):
                st.session_state.reset_step = "REQUEST"
                st.session_state.reset_token = None
                st.session_state.reset_email = None
                st.rerun()


# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    main()