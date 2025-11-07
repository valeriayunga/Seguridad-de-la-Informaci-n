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
# Guía de Configuración y Ejecución
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

### Paso 2: Instalación de Dependencias

Ejecuta el siguiente comando para instalar todas las librerías necesarias de Python:

```bash
  pip install streamlit streamlit-option-menu sqlalchemy bcrypt
```

### Paso 3: Ejecución de la Aplicación

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
