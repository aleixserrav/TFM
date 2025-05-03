import time
import paho.mqtt.client as mqtt
import servicios_sql
import modelo_prediccion


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

pred_temperatura = None
pred_humedad = None
pred_co2 = None

counter = 0

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
    global counter, temperatura, humedad, co2, backup_temperatura, backup_humedad, backup_co2, pred_temperatura, pred_humedad, pred_co2
    counter = 0
    if msg.topic == "sensores/temperatura":
        temperatura = valor
        modelo_prediccion.actualizar_modelo_con_valor_real(pred_temperatura, valor)
    elif msg.topic == "sensores/humedad":
        humedad = valor
        modelo_prediccion.actualizar_modelo_con_valor_real(pred_humedad, valor)
    elif msg.topic == "sensores/co2":
        co2 = valor
        modelo_prediccion.actualizar_modelo_con_valor_real(pred_co2, valor)
    elif msg.topic == 'sensores/backup/temperatura':
        backup_temperatura = valor
    elif msg.topic == 'sensores/backup/humedad':
        backup_humedad = valor
    elif msg.topic == 'sensores/backup/co2':
        backup_co2 = valor

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_start()


while True:
    print(f"Temperatura: {temperatura}")
    print(f"Humedad: {humedad}")
    print(f"CO2: {co2}")

    # Almacenamos los valores recibidos en la base de datos database_global
    servicios_sql.guardar_datos_database(temperatura, humedad, co2, "database_global")

    # Predecir comportamiento
    dataframe_temperatura = modelo_prediccion.obtener_datos("temperatura")
    dataframe_humedad = modelo_prediccion.obtener_datos("humedad")
    dataframe_co2 = modelo_prediccion.obtener_datos("co2")

    if dataframe_temperatura is not None and not dataframe_temperatura.empty:
        pred_temperatura = modelo_prediccion.entrenar_y_predecir(dataframe_temperatura, "temperatura")
    if dataframe_humedad is not None and not dataframe_humedad.empty:
        pred_humedad = modelo_prediccion.entrenar_y_predecir(dataframe_humedad, "humedad")
    if dataframe_co2 is not None and not dataframe_co2.empty:
        pred_co2 = modelo_prediccion.entrenar_y_predecir(dataframe_co2, "co2")

    # Detectar pérdida de la comunicación con los sensores y restablecer variables
    counter = counter + 1
    if counter >= 3:
        temperatura = None
        humedad = None
        co2 = None
    
    time.sleep(10)

