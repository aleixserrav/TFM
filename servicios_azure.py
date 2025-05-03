import pyodbc

# Instalar pyodbc
# Instalar ODBC 18 Driver: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=debian18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline
# Crear SQL Database en Azure
# CONFIGURACIÓN RED: SQL Server - Show networking settings - Public Access: Selected networks - Add your client IPv4 Address
# VER TABLAS Y DATOS: SQL Database - Query editor (preview) - Login (usd: sensores; psw: Raspberry1.) - Tables, Edit Data (Preview)


CONNECTION_STRING = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:server-sensores.database.windows.net,1433;Database=sensores-database;Uid=sensores;Pwd=Raspberry1.;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def crear_tabla_azure():
    server = 'tcp:server-sensores.database.windows.net,1433'
    database = 'sensores-database'
    username = 'sensores'
    password = 'Raspberry1.'
    driver = '{ODBC Driver 18 for SQL Server}'

    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};'
            f'UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tabla_datos')
            BEGIN
                CREATE TABLE tabla_datos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    temperatura FLOAT,
                    humedad FLOAT,
                    co2 FLOAT,
                    timestamp DATETIME DEFAULT GETDATE()
                )
            END
        """)
        conn.commit()

        print("✅ Tabla inicializada correctamente en Azure SQL Database")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error al conectar o crear la tabla: {e}")


def guardar_datos_azure(temperatura, humedad, co2):
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()

        query = """
            INSERT INTO tabla_datos (temperatura, humedad, co2)
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (temperatura, humedad, co2))
        conn.commit()

        print("✅ Datos guardados en Azure SQL correctamente")

        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"❌ Error al guardar en Azure SQL Database: {e}")