import time
import paho.mqtt.client as mqtt
import servicios_sql

# Inicialización de tópicos para suscribirse
TOPICS = ["sensores/temperatura",
          "sensores/humedad",
          "sensores/co2",
          "sensores/backup/#"]

# Inicialización de variables
temperatura = None
humedad = None
co2 = None

backup_temperatura = None
backup_humedad = None
backup_co2 = None

# Inicialización de las bases de datos MySQL
servicios_sql.crear_database("database_global")

# Callback al conectar el broker a la red
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"📡 Suscrito a {topic}")
    else:
        print(f"⚠️ Error de conexión con código {rc}")

# Callback al recibir un mensaje
def on_message(client, userdata, msg):
    valor = msg.payload.decode()
    global temperatura, humedad, co2, backup_temperatura, backup_humedad, backup_co2
    if msg.topic == "sensores/temperatura":
        temperatura = valor
    elif msg.topic == "sensores/humedad":
        humedad = valor
    elif msg.topic == "sensores/co2":
        co2 = valor
    elif msg.topic == 'sensores/backup/temperatura':
        backup_temperatura = valor
    elif msg.topic == 'sensores/backup/humedad':
        backup_humedad = valor
    elif msg.topic == 'sensores/backup/co2':
        backup_co2 = valor

# Creamos una instancia MQTT y asignamos las funciones on_connect y on_message para que se ejecuten cuando la Raspberry se connecte y cuando reciba un mensaje
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Se conecta la raspberry como cliente dentro de MQTT. Localhost significa que se connecta la propia raspberry pi en la que se ejecuta el programa por el puerto 1883
client.connect("localhost", 1883, 60)
client.loop_start()

while True:
    print(temperatura)
    print(humedad)
    print(co2)

    # Almacenar los datos recibidos en la base de datos "database_global"
    servicios_sql.guardar_datos_database(temperatura, humedad, co2, "database_global")

    time.sleep(5)

