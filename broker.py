import time
import paho.mqtt.client as mqtt
import servicios_sql as sql
import modelo_prediccion as mp


# Inicialización de tópicos para suscribirse
TOPICS = ["sensores/temperatura",
          "sensores/humedad",
          "sensores/co2",
          "sensores/backup/#"]

# Inicialización la clase SensorData
class SensorData:
    def __init__(self):
        self.temperatura = None
        self.humedad = None
        self.co2 = None
        self.backup_temperatura = None
        self.backup_humedad = None
        self.backup_co2 = None
        self.pred_temperatura = None
        self.pred_humedad = None
        self.pred_co2 = None
        self.counter = 0

data = SensorData()

# Inicialización de las bases de datos MySQL
sql.crear_database("database_global")

# Callback al conectar el broker a la red
def on_connect(client, userdata, flags, rc):
    """
    PROPÓSITO
    Esta función se suscribe a los tópicos de la lista TOPICS e imprime un mensaje de verificación si la conexión con el broker es exitosa.
    De lo contrario, muestra un mensaje de error.
    """
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"📡 Suscrito a {topic}")
    else:
        print(f"⚠️ Error de conexión con código {rc}")

# Callback al recibir un mensaje
def on_message(client, userdata, msg):
    """
    PROPÓSITO
    Esta función recibe los mensajes recibidos en los tópicos de MQTT y los asigna a las variables globales correspondientes.
    Las variables globales utilizadas se clasifican en 4 grupos:
        - Variables para almacenar la última lectura de datos ambientales: temperatura, humedad, co2
        - Variables para almacenar los datos recuperados en el tópico sensores/backup/#: backup_temperatura, backup_humedad, backup_co2
        - Variables para actualizar el modelo de predicción con la nueva lectura: pred_temperatura, pred_humedad, pred_co2
        - Variable para restablecer el contador de recepción de tópicos: counter 
    """
    valor = msg.payload.decode()
    data.counter = 0
    # Almacenar valores de la última lectura de datos ambientales
    if msg.topic == "sensores/temperatura":
        data.temperatura = valor
        mp.actualizar_modelo_con_valor_real(data.pred_temperatura, valor)
    elif msg.topic == "sensores/humedad":
        data.humedad = valor
        mp.actualizar_modelo_con_valor_real(data.pred_humedad, valor)
    elif msg.topic == "sensores/co2":
        data.co2 = valor
        mp.actualizar_modelo_con_valor_real(data.pred_co2, valor)
    # Almacenar valores recuperados
    elif msg.topic == 'sensores/backup/temperatura':
        data.backup_temperatura = valor
    elif msg.topic == 'sensores/backup/humedad':
        data.backup_humedad = valor
    elif msg.topic == 'sensores/backup/co2':
        data.backup_co2 = valor

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
    sql.guardar_datos_database(temperatura, humedad, co2, "database_global")

    # Predecir comportamiento
    dataframe_temperatura = mp.obtener_datos("temperatura")
    dataframe_humedad = mp.obtener_datos("humedad")
    dataframe_co2 = mp.obtener_datos("co2")

    if dataframe_temperatura is not None and not dataframe_temperatura.empty:
        data.pred_temperatura = mp.entrenar_y_predecir(dataframe_temperatura, "temperatura")
    if dataframe_humedad is not None and not dataframe_humedad.empty:
        data.pred_humedad = mp.entrenar_y_predecir(dataframe_humedad, "humedad")
    if dataframe_co2 is not None and not dataframe_co2.empty:
        data.pred_co2 = mp.entrenar_y_predecir(dataframe_co2, "co2")

    # Detectar pérdida de la comunicación con los sensores y restablecer variables
    counter = counter + 1
    if counter >= 3:
        temperatura = None
        humedad = None
        co2 = None
    
    time.sleep(30)

