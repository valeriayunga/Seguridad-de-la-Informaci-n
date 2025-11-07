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
