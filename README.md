##  Implementación de Requisitos de Seguridad (RS)

El sistema fue diseñado para cumplir y demostrar la implementación de **7 requisitos de seguridad **, relacionados con el ciclo de vida, acceso y monitoreo de usuarios.


| ID  | Requisito de Seguridad                                                                                 |
|-----|-------------------------------------------------------------------------------------------------------|
| RS1 | El registro de nuevos usuarios debe incluir validación. El sistema debe proporcionar el usuario y la contraseña. |
| RS2 | El control de ingreso (login) debe realizarse mediante un segundo factor de autenticación (2FA). Se optó por un código de verificación (simulado al correo). |
| RS3 | Se debe monitorear la creación de usuarios y registrar todos los accesos al sistema.                 |
| RS4 | El sistema debe permitir recuperar el usuario o contraseña en base al correo electrónico.            |
| RS5 | Un usuario puede ser dado de baja temporalmente y reactivado. No se debe permitir más de una sesión activa al mismo tiempo. |
| RS6 | El número de accesos fallidos debe ser controlado (máximo 4 intentos). Se debe registrar cada intento. |
| RS7 | El sistema debe controlar la gestión de sesión de trabajo.    

# Arquitectura del Proyecto
El proyecto está organizado en una arquitectura de capas:

```bash
AppAuth/
├── core/                  <-- CAPA DE LÓGICA DE NEGOCIO Y DATOS
│   ├── database.py        <-- Define la ESTRUCTURA de la BD (SQLAlchemy Modelos)
│   ├── security.py        <-- Hashing de Contraseñas (Bcrypt)
│   └── auth_service.py    <-- Lógica principal (Registro, Login, Reseteo, etc.)
│   └── ... (otros servicios para tokens, sesiones, admin)
├── app.py                 <-- CAPA DE PRESENTACIÓN (Interfaz Streamlit)
└── auth_practica.db       <-- CAPA DE DATOS (Se crea automáticamente al iniciar)
```
---

## Guía de Configuración y Ejecución

Sigue estos pasos para poner en marcha la aplicación en tu entorno local.

### Paso 1: Clonar el Repositorio

Abre tu terminal o Git Bash y utiliza la URL de tu repositorio:

```bash
# Clonar el repositorio
git clone https://github.com/valeriayunga/Seguridad-de-la-Informaci-n.git

# Entrar al directorio del proyecto (ajusta el nombre si es diferente en tu máquina)
cd Seguridad-de-la-Informaci-n
```
### Paso 2: Crear Entorno Virtual

Crea y activa un entorno virtual para aislar las dependencias del proyecto.
#### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
#### En macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate

```
### Paso 3: Instalación de Dependencias

Ejecuta el siguiente comando para instalar todas las librerías necesarias de Python:

```bash
  pip install streamlit streamlit-option-menu sqlalchemy bcrypt
```

### Paso 4: Ejecución de la Aplicación

Inicia la aplicación Streamlit. La primera vez que se ejecute, se creará automáticamente la base de datos auth_practica.db.

```bash
  streamlit run app.py
```
La aplicación se abrirá en tu navegador web por defecto, usualmente en:
```bash
# http://localhost:8501
```
La interfaz presenta un menú de navegación lateral a la izquierda y el área de contenido principal a la derecha. El menú permite al usuario alternar entre las funcionalidades de seguridad, como el Login, Registro, Activación de Cuenta y Recuperación de Contraseña.
<img width="940" height="508" alt="image" src="https://github.com/user-attachments/assets/706523c4-a8ee-48e8-8054-96b94457d67a" />
