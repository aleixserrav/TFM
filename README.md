# Proyecto TFM - Sistema IoT de Medición y Almacenamiento de Datos Ambientales en Aulas Educativas
## DESCRIPCIÓN DE LOS PROGRAMAS

## ADC
### API publica

```cpp
bool ADC_init();
float ADC_read(uint8_t channel);
```

### Descripcion de funciones
| Funcion | Descripcion | Retorno |
|---|---|---|
| `ADC_init()` | Inicializa el `ADS1115` en `0x48` y configura la ganancia `GAIN_ONE`. | `true` si el ADC responde; `false` si no se detecta el dispositivo. |
| `ADC_read(channel)` | Lee un canal en modo `single-ended` y devuelve el valor en voltios. | Tension leida como `float`. |

### API publica

```cpp
bool motorsInit(MicrostepMode mode);
bool motorMoveSteps(uint8_t motorId, long steps, float acceleration = 100U, float maxSpeed = 10000U);
bool motorMoveTo(uint8_t motorId, long position, float acceleration = 100U, float maxSpeed = 10000U);
bool motorStartSpeed(uint8_t motorId, float speed);
bool motorStop(uint8_t motorId);
bool motorsStopAll();
bool motorIsRunning(uint8_t id);
bool motorsAnyRunning();
```

### Descripcion de las funciones

|---|---|---|
| `motorsInit` | Configura microstepping, inicializa los recursos necesarios y crea una tarea FreeRTOS para el control de los motores. | `true` si se ha inicializado correctamente, `false`si ha fallado la inicializacion. |
| `motorMoveSteps`| Mueve el motor un numero de pasos determinado a la aceleracion y velocidad maxima indicadas. | `true` si el comando se acepta y se encola, `false` si el motor esta ocupado, los parametros son invalidos o falla la cola. |

### broker.py
Es el archivo principal de la Raspberry Pi que hace de broker. Su función es suscribirse a los tópicos que envia la Raspberry de los sensores, leer esos datos y almacenarlos en una base de datos local utilizando MariaDB

### main.py
Es el archivo principal de la Raspberry Pi conectada a los sensores. Su función es leer los datos de temperatura, humedad relativa y co2 de los sensores, almacenarlos en una base de datos local utilizando MariaDB, publicar esos datos en los tópicos pertinentes en MQTT (conectándose a la misma VPN que el broker mediante una IP privada) y almacenar los datos en Azure (SQL Database).

### modelo_prediccion.py
Contiene un modelo de predicción caja gris muy simplificado para predecir las siguientes muestras de los sensores basándose en datos pasados (regresión lineal) y en los errores cometidos en predicciones pasadas.

### servicios_azure.py
Programa que implementa una función para crear una tabla de datos en azure (llamada 'tabla_datos') que contiene 3 colunas (temperatura, humedad y co2) y para escribir datos de temperatura, humedad y co2 dentro de esa tabla.

### servicios_sql.py
Programa que utiliza mariaDB (es lo mismo que MySQL para Raspberry Pi) para crear una base de datos en el dispositivo local (el nombre de la base de datos es el parámetro de la función), otra función utilizada para guardar datos de temperatura, humedad y co2 dentro de esa base de datos (pasando el nombre de la base de datos como parámetro) y otra función que lee las últimas 5  muestras de un dato (especificado como parámetro al llamar la función) y devuelve el promedio de esas 5 muestras. Se utiliza para obtener un dato válido como lectura en el caso de una  lectura errónea.

### servicios_csv.py
Actualmente obsoleto y no se utiliza. Contiene funciones para escribir datos en un archivo csv (si el archivo no existe lo crea) y para obtener el promedio de las últimas 5 muestras del dato especificado como parámetro ('temperatura', 'humedad' o 'co2'). También contiene una parte que antes estaba en el programa main.py que se encargaba de guardar las lecturas en 3 archivos csv: Un archivo para muestras obtenidas 1 minuto, otro archivo para muestras obtenidas cada 5 minutos y otro archivo para muestras obtenidas cada 10 minutos.

## IMPORTANTE
Para que los programas broker.py y main.py funcionen correctamente es necesario que, dentro de la misma carpeta, estén también los programas servicios_azure.py y servicios_sql.py, ya que ambos programas
requieren de las funciones que contienen esos archivos.
