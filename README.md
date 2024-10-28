
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
6. [Ejecutar la Aplicación](#ejecutar-la-aplicación)

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
- Pipenv (`pip install pipenv`)

---

## Guía de Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <URL_del_repositorio>
   cd <nombre_del_directorio>
   ```

2. **Configura el entorno virtual**:
   Navega al directorio del proyecto y ejecuta:
   ```bash
   pipenv install --three
   ```

3. **Instala las dependencias**:
   ```bash
   pipenv install -r requirements.txt
   ```
4. **Activacion**: Cada vez que quieras activar el entorno virtual,navega hasta la carpeta donde se encuentre el venv y  ejecuta:
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
   mysql -u root -p
    ```

3. **Después de ejecutar este comando, se te pedirá que ingreses la contraseña de root:**

    Crea el usuario y otorga privilegios: Una vez dentro de MySQL, ejecuta los siguientes comandos uno por uno para crear el usuario y otorgarle los permisos necesarios sobre la base de datos Grupo_4_bowling:

    ```sql
    CREATE USER 'admin'@'localhost' IDENTIFIED BY 'TPI-6to-bowling';
    GRANT ALL PRIVILEGES ON Grupo_4_bowling.* TO 'admin'@'localhost';
    FLUSH PRIVILEGES;
    ```

4. **Salir de MySQL: Cuando hayas terminado, escribe exit para salir de MySQL.**

    ```sql
        exit
    ```


---

## Configura y ejecuta la Aplicación

1. **Comenzamos creando un SuperUsuario**:

   ```bash
   python manage.py createsuperuser
   ```

   Luego te va a pedir un nombre de **usuario**, **mail** y **password**. Es importante que recuerdes el email y password  para poder iniciar sesion como Administrador luego en la Aplicacion.


1. **Aplica las migraciones**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Vamos a generar los Registros en la base de datos**
    primero nos loggeamos en sql con el usuario **admin** que creamos anteriormente

    ```bash
        mysql -u admin -p
    ```

    colocamos la **password** de antes, y despues copiamos y pegamos este codigo para poder generar todos los registros ncesarios:

    ```sql
    
    INSERT INTO main_estadopartida (estado, descripcion) VALUES
    ('Bloqueada', 'Debes Jugar las partidas anteriores antes de poder iniciar esta.'),
    ('Cancelada', 'La partida tuvo que ser cancelada.'),
    ('Disponible', 'Partida reservada con exito, pero aun no ha comenzado.'),
    ('En proceso', 'La partida se esta jugando ahora mismo.'),
    ('Finalizada', 'La partida termino con exito, dando a un ganador.'),
    ('Pausada', 'La partida fue pausada por algun motivo.');

    
    INSERT INTO main_estadopedido (estado, descripcion) VALUES
    ('Cancelado', 'Tu pedido tuvo que ser cancelado :('),
    ('En proceso', 'Estan preparando tu pedido'),
    ('Entregado', 'Ya lo podes disfrutar'),
    ('Pedido Confirmado', 'El pedido ya llego a la cocina y lo estan por preparar.'),
    ('Terminado', 'Lo estan por llevar a tu mesa');

    
    INSERT INTO main_estadopista (estado, descripcion) VALUES
    ('Disponible', 'La pista esta lista para poder ser usada'),
    ('Mantenimiento', 'Estamos arreglando/limpiando la pista, estara lista pronto!');

    
    INSERT INTO main_estadoreserva (estado, descripcion) VALUES
    ('Cancelada', 'Tu reserva fue cancelada :('),
    ('Confirmada', 'Reserva confirmada con exito, te esperamos pronto!'),
    ('En curso', 'Ya es el dia y la hora de tu reserva, a jugar!!'),
    ('Finalizada', 'Gracias por venir a Strike Zone, los esperamos pronto');

    
    INSERT INTO main_historialestado (fecha_hora_inicio, fecha_hora_fin, estado_id, id_reserva_id) VALUES
    ('2024-10-28 11:21:23.938141', '2024-10-28 08:21:00.000000', 'Confirmada', 134),
    ('2024-10-28 11:21:23.975564', '2024-10-28 13:21:23.975564', 'En curso', 134),
    ('2024-10-28 11:25:48.648161', '2024-10-28 11:25:48.648182', 'Finalizada', 134);

    
    INSERT INTO main_producto (nombre, descripcion, precio) VALUES
    ('Nachos con Cheddar', 'un clasico Mexicano', 2000),
    ('Hamburguesa', 'La clasica de la casa', 3000),
    ('Coca Cola', 'Refrescante', 1000);

    
    INSERT INTO main_pistabowling (capacidad_maxima, descripcion, estado_id) VALUES
    (10, 'Pista 1', 'Disponible'),
    (10, 'Pista 2', 'Disponible'),
    (10, 'Pista 3', 'Disponible'),
    (10, 'Pista 4', 'Disponible'),
    (10, 'Pista 5', 'Disponible'),
    (10, 'Pista 6', 'Disponible'),
    (10, 'Pista 7', 'Disponible');
    ```

2. **Ejecuta el servidor**:

   ```bash
   python manage.py runserver
   ```

3. **Accede a la aplicación**:

   La aplicación estará disponible en [http://localhost:8000](http://localhost:8000).
---




