import time
import servicios_sql
import datetime
import board
import busio
import adafruit_scd30
from dht20_sensor.sensor import DHT20Sensor
import paho.mqtt.client as mqtt
import mysql.connector

BROKER_IP = "100.113.130.118"

# Inicialización variables
inicio_1 = datetime.datetime.now()
inicio_5 = datetime.datetime.now()
inicio_10 = datetime.datetime.now()

# Función para obtener los datos de los sensores
def get_sensors_data():
    try:
        temperatura, humedad = sensor_DHT20.read()
    except:
        # Si no se consiguen datos del sensor, leer promedio de las últimas 5 muestras
        temperatura = servicios_sql.obtener_media("temperatura")
        humedad = servicios_sql.obtener_media("humedad")

    try:
        co2 = sensor_SCD30.CO2
    except:
        co2 = servicios_sql.obtener_media("co2")

    return temperatura, humedad, co2

def on_connect(client, userdata, flags, rc):
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
#client.connect(BROKER_IP, 1883, 60)

# Inicialización I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicialitzación de los sensores
sensor_DHT20 = DHT20Sensor()
sensor_SCD30 = adafruit_scd30.SCD30(i2c)

# Inicialización de las bases de datos MySQL
servicios_sql.crear_database("database_sensores")
servicios_sql.crear_database("database_backup")


while True:
        # Llegir dades dels sensors
        t, h, co2 = get_sensors_data()
        string_temperatura = str(t)
        string_humedad = str(h)

        temperatura = float(string_temperatura.rstrip("C"))
        humedad = float(string_humedad.rstrip("%"))

        print(temperatura)
        print(humedad)
        print(co2)

        # Publicar dades al broker
        #client.publish("sensores/temperatura", tf)
        #client.publish("sensores/humedad", hf)
        #client.publish("sensores/co2", co2)

        # Guardar dades a MySQL
        servicios_sql.guardar_datos_database(temperatura, humedad, co2, "database_sensores")
        if not client.is_connected():
            servicios_sql.guardar_datos_database(temperatura, humedad, co2, "database_backup")

        time.sleep(5)