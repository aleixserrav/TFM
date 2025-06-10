import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import deque

errores_recientes = deque(maxlen=10)

# Parámetros de conexión a MariaDB
config = {
    'user': 'grafana',
    'password': 'grafana',
    'host': 'localhost',
    'port': 3306,
    'database': 'database_global'
}

def actualizar_modelo_con_valor_real(predicho, real):
    """
    PROPÓSITO
    Esta función verifica la validez de los datos, calcula el error cometido por el modelo y lo guarda en un deque de longitud 10.

    PARÁMETROS
    predicho: Variable tipo float que indica la última predicción calculada por el modelo.
    real: Variable tipo float que indica el valor ambiental real leído por el sensor.
    """
    if real is None:
        print("⚠️ Valor real es None, no se actualiza el modelo.")
        return
    if predicho is None:
        print("⚠️ Valor predicho es None, no se actualiza el modelo.")
        return

    real = (float(real))
    error = real - predicho
    errores_recientes.append(error)


def obtener_datos_locales(parametro_ambiental):
    """
    PROPÓSITO
    Esta función obtiene los 10 últimos valores del parámetro ambiental seleccionado de la base de datos SQL local (database_global).
    Si la lectura se realiza con éxito se muestra un mensaje de verificación. De lo contrario muestra un mensaje de error.

    PARÁMETROS
    parametro_ambiental: Variable tipo string que indica el parámetro ambiental del cual se quieren obtener los datos. Puede ser:
        - 'temperatura'
        - 'humedad'
        - 'co2' """
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        query = f"""
            SELECT {parametro_ambiental}, timestamp
            FROM tabla_datos
            ORDER BY timestamp DESC
            LIMIT 10
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=[f"{parametro_ambiental}", "timestamp"])
        df = df.sort_values(by="timestamp")

        return df

    except Exception as e:
        print(f"❌ Error al obtener datos de {parametro_ambiental}: {e}")
        return None


def entrenar_y_predecir(df, parametro_ambiental):
    """
    PROPÓSITO
    Entrenar un modelo de regresión lineal para predecir la siguiente muestra del parámetro ambiental especificado.
    Si la predicción se realiza con éxito, imprime un mensaje en la terminal indicando el valor predicho.
    Si la predicción falla, se imprime un mensaje de error.
    
    PARÁMETROS
        - df: Un DataFrame que contiene los últimos 10 datos del parámetro ambiental.
        - parametro_ambiental: Variable tipo string que indica qué columna del DataFrame se va a utilizar como variable objetivo para el modelo.
    """
    try:
        # Creamos una secuencia simple: [0, 1, 2, ..., N-1] como "tiempo"
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[f"{parametro_ambiental}"].values

        model = LinearRegression()
        model.fit(X, y)

        # Predecimos el siguiente punto
        next_time = np.array([[len(df)]])
        pred = model.predict(next_time)[0]

        # Aplicar corrección si hay errores recientes
        if errores_recientes:
            correccion = np.mean(errores_recientes)
            pred -= correccion

        if parametro_ambiental == "temperatura":
            print(f"🔮 Predicción de temperatura para el siguiente instante: {pred:.2f} °C")
        if parametro_ambiental == "humedad":
            print(f"🔮 Predicción de humedad para el siguiente instante: {pred:.2f} %")
        if parametro_ambiental == "co2":
            print(f"🔮 Predicción de co2 para el siguiente instante: {pred:.2f} ppm")
        return pred

    except Exception as e:
        print(f"❌ Error al predecir la siguiente muestra: {e}")
        return None
