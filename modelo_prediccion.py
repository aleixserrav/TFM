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
    if real is None:
        print("⚠️ Valor real es None, no se actualiza el modelo.")
        return
    if predicho is None:
        print("⚠️ Valor predicho es None, no se actualiza el modelo.")
        return

    real = (float(real))
    error = real - predicho
    errores_recientes.append(error)

def obtener_datos(parametro):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        query = f"""
            SELECT {parametro}, timestamp
            FROM tabla_datos
            ORDER BY timestamp DESC
            LIMIT 10
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=[f"{parametro}", "timestamp"])
        df = df.sort_values(by="timestamp")

        return df

    except Exception as e:
        print(f"❌ Error al obtener datos de {parametro}: {e}")
        return None

def entrenar_y_predecir(df, parametro):
    try:
        # Creamos una secuencia simple: [0, 1, 2, ..., N-1] como "tiempo"
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[f"{parametro}"].values

        model = LinearRegression()
        model.fit(X, y)

        # Predecimos el siguiente punto
        next_time = np.array([[len(df)]])
        pred = model.predict(next_time)[0]

        # Aplicar corrección si hay errores recientes
        if errores_recientes:
            correccion = np.mean(errores_recientes)
            pred += correccion

        if parametro == "temperatura":
            print(f"🔮 Predicción de temperatura para el siguiente instante: {pred:.2f} °C")
        if parametro == "humedad":
            print(f"🔮 Predicción de humedad para el siguiente instante: {pred:.2f} %")
        if parametro == "co2":
            print(f"🔮 Predicción de co2 para el siguiente instante: {pred:.2f} ppm")
        return pred

    except Exception as e:
        print(f"❌ Error al predecir la siguiente muestra: {e}")
        return None