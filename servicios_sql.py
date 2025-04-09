import mysql.connector
# mysql -u root -p
# USE database_sensores;
# SELECT * FROM tabla_datos;


def crear_database(nombre_db):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
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
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
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


def obtener_media(parametro):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="broker",
            database="sensores_data"
        )

        cursor = db.cursor()

        if parametro == 'temperatura':
            columna = 'temperatura'
        elif parametro == 'humedad':
            columna = 'humedad'
        elif parametro == 'co2':
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