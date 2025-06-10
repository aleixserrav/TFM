import time
import board
import busio
import adafruit_scd30
from dht20_sensor.sensor import DHT20Sensor
import paho.mqtt.client as mqtt
import mysql.connector
import servicios_sql as sql
import servicios_azure as azure

BROKER_IP = "100.81.19.80"


# Función para obtener los datos de los sensores
def obtener_datos_sensores():
    """"
    PROPÓSITO
    Leer los valores de CO2, temperatura y humedad utilizando las librerías de los sensores SCD30 y DHT20.
    En caso de producirse un error, el valor se obtiene calculando la media de los últimos 5 valores registrados.
    
    VALOR DEVUELTO
    La función devuelve una tupla que contiene los 3 parámetros ambientales, por ejemplo (21.5C, 47.5%, 850)
    """
    try:
        temperatura, humedad = sensor_DHT20.read()
    except:
        temperatura = sql.obtener_promedio_5_ultimos_valores("temperatura")
        humedad = sql.obtener_promedio_5_ultimos_valores("humedad")

    try:
        co2 = sensor_SCD30.CO2
    except:
        co2 = sql.obtener_media("co2")

    return temperatura, humedad, co2


def on_connect(client, userdata, flags, rc):
    """
    PROPÓSITO
    Establecer conexión con la base de datos de recuperación (database_backup) y publicar los datos que contiene por MQTT.
    Una vez asegurado su envío, los datos se eliminan y se muestra un mensaje de verificación. 
    En caso de producirse un error al establecer la conexión se muestra un mensaje de error.
    """
    if rc == 0:
        try:
            # Conectar a la base de datos
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="broker",
                database="database_backup"
            )
            cursor = db.cursor()

            # Obtener los datos almacenados en la tabla 'tabla_datos'
            query = "SELECT id, temperatura, humedad, co2 FROM tabla_datos"
            cursor.execute(query)
            resultados = cursor.fetchall()

            # Publicar los datos en el broker MQTT
            for row in resultados:
                # Publicar cada dato en su respectivo tópico
                id_dato, temperatura, humedad, co2, timestamp = row
                client.publish("sensores/backup/temperatura", temperatura)
                client.publish("sensores/backup/humedad", humedad)
                client.publish("sensores/backup/co2", co2)
                client.publish("sensores/backup/timestamp", timestamp)

                # Eliminar el dato después de enviarlo
                cursor.execute("DELETE FROM tabla_datos WHERE id = %s", (id_dato,))
            
            db.commit()
            cursor.close()
            db.close()
        
        except mysql.connector.Error as err:
            print(f"❌ Error al conectar con la base de datos database_backup: {err}")

    else:
        print(f"⚠️ Error de conexión con el broker {rc}")

# Inicialización cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER_IP, 1883, 60)

# Inicialización I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicialitzación de los sensores
sensor_DHT20 = DHT20Sensor()
sensor_SCD30 = adafruit_scd30.SCD30(i2c)

# Inicialización de las bases de datos MySQL
sql.crear_database("database_sensores")
sql.crear_database("database_backup")

# Inicialización de las bases de datos en la nube (Azure)
azure.crear_tabla_datos_en_azure()


while True:
        t, h, co2 = obtener_datos_sensores()
        string_temperatura = str(t)
        string_humedad = str(h)

        temperatura = float(string_temperatura.rstrip("C"))
        humedad = float(string_humedad.rstrip("%"))

        print(temperatura)
        print(humedad)
        print(co2)

        # Publicar datos al broker
        client.publish("sensores/temperatura", temperatura)
        client.publish("sensores/humedad", humedad)
        client.publish("sensores/co2", co2)

        # Guardar datos a MySQL
        sql.guardar_datos_database(temperatura, humedad, co2, "database_sensores")
        if not client.is_connected():
            sql.guardar_datos_database(temperatura, humedad, co2, "database_backup")

        # Guardar datos a Azure SQL Database
        azure.guardar_datos_azure(temperatura, humedad, co2)

        time.sleep(30)