
# Grupo 4 - Centro de Bowling

## Integrantes del Grupo:
- MARTINO, Nahuel
- PAGANI, Nicolas
- VERCELLONE, Carlos Ignacio
- ZABALA, Valentin

---

## Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Estructura del Repositorio](#estructura-del-repositorio)
3. [Requisitos Previos](#requisitos-previos)
4. [Guía de Instalación](#guía-de-instalación)
5. [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
6. [Ejecutar la Aplicación](#configura-y-ejecuta-la-aplicación)

---

## Descripción del Proyecto

Este es un proyecto Django para la gestión de un centro de bowling. La aplicación permite a los usuarios gestionar reservas, visualizar información de jugadores, y administrar puntuaciones.

---

## Estructura del Repositorio

```plaintext
├── Diagrama de Clases
│   ├── CentroDeBowling_4.mmd
│   └── CentroDeBowling_4.png
├── E-R Diagram
│   ├── CentroDeBowling_4.mmd
│   └── CentroDeBowling_4.png
├── MYSQL
│   ├── CentroDeBowling_4-mysql.sql
│   └── Centro_de_bowling.mwb
├── VENV Proyecto
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── Proyecto_Integrador
│   │   ├── config
│   │   ├── db.sql
│   │   ├── main
│   │   └── manage.py
│   └── requirements.txt
```

---

## Requisitos Previos

Asegúrate de tener instalados los siguientes componentes en tu sistema:
- Python 3.8+
- Pip
- MySQL Server
- **Pipenv (`pip install pipenv`)**

- **Para evitar futuros conflictos**
   ```bash 
      sudo apt update
      sudo apt upgrade
   ```

---

## Guía de Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <URL_del_repositorio>
   cd <nombre_del_directorio>
   ```

2. **Configura el entorno virtual**:
   Navega al directorio **VENV + DJANGO** y ejecuta:
   ```bash
   pipenv install
   ```
   Esto  creará un entorno virtual y lo configurará con las dependencias especificadas.

3. **Activacion**: Cada vez que quieras activar el entorno virtual,navega hasta la carpeta donde se encuentre el venv y  ejecuta:
   ```bash
   pipenv shell
   ```


---

## Configuración de la Base de Datos



## Iniciar MySQL y Crear el Usuario

1. **Abre la terminal o símbolo del sistema**.

2. **Accede a MySQL como usuario root**:
   Cuando instalaste MySQL, debiste haber configurado una contraseña para el usuario `root`. Usa esa contraseña para acceder.

   ```bash
   sudo mysql -p
    ```

3. **Después de ejecutar este comando, se te pedirá que ingreses la contraseña de root:**

    Crea el usuario y otorga privilegios: Una vez dentro de MySQL, ejecuta los siguientes comandos uno por uno para crear el usuario y otorgarle los permisos necesarios sobre la base de datos Grupo_4_bowling:

    ```sql
    CREATE DATABASE IF NOT EXISTS Grupo_4_bowling;
    CREATE USER 'admin'@'localhost' IDENTIFIED BY 'TPI-6to-bowling';
    GRANT ALL PRIVILEGES ON Grupo_4_bowling.* TO 'admin'@'localhost';
    FLUSH PRIVILEGES;
    ```

4. **Salir de MySQL: Cuando hayas terminado, escribe exit para salir de MySQL.**

    ```sql
        exit
    ```


---

## Importar Datos al Iniciar el Proyecto

Navega primero al directorio del proyecto Django 

```bash
cd VENV\ +\ DJANGO/Proyecto_Integrador/
```

Para que los datos se carguen automáticamente, puedes añadir el siguiente comando en tu script de inicialización o en la documentación para ejecutarlo al iniciar el proyecto:

```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
Django aplicara las migraciones de datos


```bash
python manage.py loaddata database.json
```

Django cargará los datos especificados en la base de datos del proyecto.


---

## Configura y ejecuta la Aplicación

1. **Datos del Usuario Administrador**:

   ```python
   email: grupo4@admin.com
   password: admin
   ```

   Es importante que recuerdes el email y password  para poder iniciar sesion como Administrador luego en la Aplicacion.


1. **Ejecuta el servidor**:

   ```bash
   python manage.py runserver
   ```

3. **Accede a la aplicación**:

   La aplicación estará disponible en [http://localhost:8000](http://localhost:8000).
---
