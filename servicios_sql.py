import mysql.connector
# mysql -u root -p
# USE database_sensores;
# SELECT * FROM tabla_datos;


def crear_database(nombre_db):
    """
    PROPÓSITO
    Esta función crea una base de datos MySQL dentro del usuario 'grafana' si todavía no existe y la tabla 'tabla_datos'.
    En caso de no haber fallos, imprime un mensaje de verificación. Si hay fallos imprime un mensaje de error.

    PARÁMETROS
    nombre_db: El nombre de la base de datos (string)
    """
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="grafana",
            password="broker"
        )
        cursor = db.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_db}")
        cursor.execute(f"USE {nombre_db}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tabla_datos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                temperatura FLOAT,
                humedad FLOAT,
                co2 FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print(f"✅ Base de datos {nombre_db} y tabla creadas o ya existentes")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"❌ Error al conectarse a la base de datos: {err}")


def guardar_datos_database(temperatura, humedad, co2, nombre_db):
    """
    PROPÓSITO
    Esta función almacena los 3 valores ambientales (temperatura, humedad y co2) en la base de datos asignada por el parámetro nombre_db.
    Si la inserción se realiza con éxito, muestra un mensaje de verificación. En caso contrario muestra un mensaje de error.

    PARÁMETROS
    temperatura, humedad, co2: Variables tipo float correspondientes a los valores ambientales leídos por los sensores
    nombre_db: Variable tipo string que indica la base de datos a la que se quieren añadir los datos
    """
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="grafana",
            password="broker",
            database=nombre_db
        )
        cursor = db.cursor()
        query = "INSERT INTO tabla_datos (temperatura, humedad, co2) VALUES (%s, %s, %s)"
        cursor.execute(query, (temperatura, humedad, co2))
        db.commit()
        cursor.close()
        db.close()
        print(f"✅ Datos guardados correctamente en la base de datos {nombre_db}")
    except mysql.connector.Error as err:
        print(f"❌ Error al guardar en la base de datos: {err}")


def obtener_promedio_5_ultimos_valores(parametro_ambiental):
    """
    PROPÓSITO
    Leer los últimos 5 registros del parámetro ambiental solicitado y devolver el promedio. Si la lectura se realiza con éxito, la función
    imprime un mensaje de verificación. En caso contrario muestra un mensaje de error.

    PARÁMETROS
    parametro_ambiental: Variable tipo string que indica el parámetro ambiental del cual se quiere calcular el promedio. Las opciones son:
        - 'temperatura'
        - 'humedad'
        - 'co2'

    VALOR DEVUELTO
    Devuelve una variable tipo float que contiene el promedio del parámetro seleccionado, por ejemplo 22.5 para el parámetro 'temperatura'
    """
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="broker",
            database="sensores_data"
        )

        cursor = db.cursor()

        if parametro_ambiental == 'temperatura':
            columna = 'temperatura'
        elif parametro_ambiental == 'humedad':
            columna = 'humedad'
        elif parametro_ambiental == 'co2':
            columna = 'co2'
        else:
            raise ValueError("❌ Parámetro inválido. Debe ser 'temperatura', 'humedad' o 'co2'.")

        query = f"SELECT {columna} FROM tabla_datos ORDER BY id DESC LIMIT 5;"
        cursor.execute(query)
        
        resultados = cursor.fetchall()

        if resultados:
            suma = sum([x[0] for x in resultados])
            promedio = suma / len(resultados)
        else:
            promedio = None

        cursor.close()
        db.close()

        return promedio

    except mysql.connector.Error as err:
        print(f"❌ Error al obtener la media de {parametro}: {err}")
        return None