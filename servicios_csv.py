import csv
import datetime


# Guardar les dades en un arxiu csv
def write_to_csv(nom_arxiu, temperatura, humedad, Co2):
    now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(nom_arxiu, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([now, temperatura, humedad, Co2])



def leer_5_ultimas_muestras(filename, dada):
    valores = []
    try:
        with open(filename, mode='r') as file:
            reader = list(csv.reader(file))

            if len(reader) > 0:
                for row in reader[-5:]:
                    try:
                        if dada == 'temperatura':
                            valores.append(float(row[1].replace('C', '')))
                        elif dada == 'humedad':
                            valores.append(float(row[2].replace('%', '')))
                        elif dada == 'co2':
                            valores.append(float(row[3]))
                    except:
                        pass

                promedio = sum(valores) / len(valores)

            else:
                promedio = None

    except:
        promedio = None

    return promedio

    # Guardar dades cada 1 minut
        """ahora = datetime.datetime.now()
        if (ahora - i"nicio_1) >= datetime.timedelta(minutes=1):
                if temperatura is not None and humedad is not None and co2 is not None:
                    servicios_csv.write_to_csv('sensor_data_1min.csv', temperatura, humedad, co2)
                    inicio_1 = ahora

        # Guardar dades cada 5 minuts
        if (ahora - inicio_5) >= datetime.timedelta(minutes=5):
                if temperatura is not None and humedad is not None and co2 is not None:
                    servicios_csv.write_to_csv('sensor_data_5min.csv', temperatura, humedad, co2)
                    inicio_5 = ahora

        # Guardar dades cada 10 minuts
        if (ahora - inicio_10) >= datetime.timedelta(minutes=10):
                if temperatura is not None and humedad is not None and co2 is not None:
                    servicios_csv.write_to_csv('sensor_data_10min.csv', temperatura, humedad, co2)
                    inicio_10 = ahora"""