from xml.dom import minidom
import psycopg2 as psql
import json
import pandas as pd
import requests
import numpy as np
from datetime import date, datetime
import geopandas as gpd
from notificador import Notificador
import sys
        
# Establecer en True para cargar todos los datos desde cero, e imprimir logs
DEBUG = False

def consoleLog(text):
    if DEBUG:
        print(text)

def getConnection(  user, password, host, port, db):
    connection = None
    connection = psql.connect(user = user,  password = password,
                    host = host, port = port, database = db)
    return connection

def getAuthConnection():
    return getConnection('covid', '@cov19@platfTf119!', '163.178.101.94', '8080', 'covidinfo')
    #return getConnection('postgres', 'password', 'localhost', '5432', 'postgres')

def closeConnection(connection):
    if connection:
        connection.close()

# Carga los casos por día para cada distrito en cada fecha
def cargarCasosDiarios(df, ultimaFecha):
    conn = getAuthConnection()
    cursor = conn.cursor()
    #las fechas empiezan en la columna 6
    COL_OFFSET = 6
    COL_COD_DISTRITO = 4
    ordenes_cargadas = False

    #para cada fila sin contar encabezado
    for row in range( 1, df.shape[0]) : 
        #para cada fecha
        for col in range(COL_OFFSET, COL_OFFSET + len(df.iloc[0, COL_OFFSET:])):
            if not pd.isnull(df.iloc[row, col]):
                fecha = str(df.iloc[0, col]).split(' ')[0]
                if fecha > ultimaFecha or DEBUG == True:
                    if not ordenes_cargadas:
                        try:
                            cargarDenuncias(fecha)
                        except Exception as e:
                            consoleLog(e)
                    q = """
                        UPDATE acumulado_distrito 
                        SET caso_dia = {cantidad}
                        WHERE codigo_distrito = '{codigo}'
                        AND fecha = '{fecha}'"""

                    #carga los casos por día si es mayor que 0 para cada distrito en cada fecha
                    query = q.format(
                        cantidad = df.iloc[row, col] if df.iloc[row, col] >= 0 else 0, 
                        codigo = df.iloc[row, COL_COD_DISTRITO], 
                        fecha = fecha)
                    try:
                        cursor.execute(query)
                        conn.commit()
                    except Exception as e:
                        consoleLog(e)
                        raise
        ordenes_cargadas = True
                    
        consoleLog("Cargando casos nuevos para el distrito: " + str(df.iloc[row, COL_COD_DISTRITO]))
            
    closeConnection(conn)

# Carga los casos activos, acumulados, fallecidos, recuperados para todos los distritos y todas las fechas
def cargarCasos(archivo, ultimaFecha):
    consoleLog("Leyendo archivo de casos...")
    df = pd.read_excel(archivo, header= None, sheet_name="Desagre_Distrito", usecols="G,I,N,R,V,Z")
    consoleLog("archivo de casos leído")
    try:
        conn = getAuthConnection()
        cursor = conn.cursor()

        #para cada fila sin contar encabezado
        for row in range(1, df.shape[0]) : 
            fecha = str(df.iloc[row, 1]).split(' ')[0]
            if fecha > ultimaFecha or DEBUG == True:
                q = """
                        INSERT INTO acumulado_distrito (fecha, codigo_distrito, recuperados, cantidad, fallecidos, activos)
                        VALUES ('{fecha}', {codigo}, {recuperados}, {cantidad}, {fallecidos}, {activos}) ON CONFLICT DO NOTHING;"""
                query = q.format(
                    codigo = df.iloc[row, 0], 
                    fecha = fecha,
                    cantidad = df.iloc[row, 2] if df.iloc[row, 2] >= 0 else 0, 
                    recuperados = df.iloc[row, 3] if df.iloc[row, 3] >= 0 else 0, 
                    fallecidos = df.iloc[row, 4] if df.iloc[row, 4] >= 0 else 0, 
                    activos = df.iloc[row, 5] if df.iloc[row, 5] >= 0 else 0, 
                )
                cursor.execute(query)
                consoleLog  ("-----------------------")
                consoleLog (fecha)
                consoleLog  ("-----------------------")
                conn.commit()  
    except (Exception, psql.Error) as error :
                consoleLog("Error while connecting to PostgreSQL" + error)
                raise
            
    closeConnection(conn)

# Carga el coeficiente de variación para cada distrito y cada semana epidemiológica, según la definición del Ministerio de Salud.
def cargarCoefVar(archivoCovid, ultimaFecha):
    df = pd.read_excel(archivoCovid, header= None, sheet_name="3_4 DIST_ACTIV")
    dfNuevos = pd.read_excel(archivoCovid, header= None, sheet_name="DistritosNuevos")
    conn = getAuthConnection()
    cursor = conn.cursor()
    COL_OFFSET = 6
    COL_COD_DISTRITO = 4
    semanaAnterior = 0
    coef_var = 0
    tasa_ataque = 0
    #para cada distrito (fila)
    for row in range(1, df.shape[0]) : 
        #para cada fecha
        codigo = df.iloc[row, COL_COD_DISTRITO]
        if not str(codigo).endswith('99'):
            for col in range(COL_OFFSET, COL_OFFSET + len(df.iloc[0, COL_OFFSET:])):
                q = """
                    UPDATE acumulado_distrito 
                    SET coef_var = {coef_var},
                    ta = {tasa_ataque}
                    WHERE codigo_distrito = '{codigo}'
                    AND fecha = '{fecha}'"""

                # Hace split porque contiene también la hora, y no es necesaria.
                fecha = str(df.iloc[0, col]).split(' ')[0]
                if True: #fecha > ultimaFecha or DEBUG == True:                    
                    semanaActual = numeroSemanaEpidemiologica(fecha)
                    anoActual = fecha.split('-')[0]

                    # El coeficiente se asocia a cada semana, por eso se calcula solo una vez
                    if semanaActual != semanaAnterior:
                        coef_var = 0
                        tasa_ataque = 0
                        coef_var = calcularCoefVar(row, semanaActual, anoActual, df)
                        tasa_ataque = calcularTasaAtaque(row, semanaActual, anoActual, dfNuevos)
                        semanaAnterior = semanaActual

                    # Multiplica por 100 porque es un porcentaje, y redondea a dos decimales
                    query = q.format(
                        coef_var = round(coef_var * 100, 2),
                        codigo = codigo, 
                        tasa_ataque = tasa_ataque,
                        fecha = fecha)

                    cursor.execute(query)
                    conn.commit()  
            consoleLog("Cargando coef_var y ta para distrito: " + str(codigo))
    closeConnection(conn)

# Calcula el coeficiente de variación dada una fila de un distrito, la semana epidemiológica y el data frame.
def calcularCoefVar(distrito, semana, ano, df):

    #Si la semana es la 25 del 2020, no se puede calcular porque no hay datos antes de esa seamana, y se retorna 0.
    if semana < 28 and int(ano) == 2020:
        return 0

    semanaCalculo = 0
    casosSemanasAnteriores = []
    anoActual = 0
    for i in range(1, 4):
        if semana - i < 0:
            anoActual = str(int(ano) - 1)
            maxSemana = numeroSemanaEpidemiologica(anoActual + "-12-31")
            semanaCalculo = maxSemana + 1 - i
        else:
            anoActual = ano
            semanaCalculo = semana - i
        # se crea un arreglo con la cantidad de casos activos de las últimas 3 semanas epidemiológicas anteriores a la semana dada
        casosSemanasAnteriores.append(sumarCasosSemana(distrito, semanaCalculo, anoActual, df))

    # Se realiza el cálculo de la desviación estándar y la media aritmética
    sd = np.std(casosSemanasAnteriores)
    mean = np.mean(casosSemanasAnteriores)

    # Evita dividir entre 0
    if sd == 0 or mean == 0:
        return 0
    else:
        return sd/mean

def calcularTasaAtaque(distrito, semana, ano, df):

    #Si la semana es la 25 del 2020, no se puede calcular porque no hay datos antes de esa seamana, y se retorna 0.
    if semana < 26 and int(ano) == 2020:
        return 0

    # Se realiza el cálculo de la desviación estándar y la media aritmética
    suma = sumarCasosSemana(distrito, semana, ano, df)

    conn = getAuthConnection()
    cursor = conn.cursor()
    query = "select poblacion from datos_distrito where codigo_distrito = '{codigo}'"
    if str(df.iloc[distrito, 4]).endswith('99'):
        return 0
    codigo = df.iloc[distrito, 4]
    cursor.execute(query.format(codigo = df.iloc[distrito, 4]))
    poblacion = 0
    try:
        poblacion = cursor.fetchone()[0]
    except:
        consoleLog("Error, no hay datos de población para el distrito código: " + str(codigo))
    conn.close()

    # Evita dividir entre 0
    if poblacion == 0:
        return 0
    else:
        return (suma/poblacion) * 100
    

# Obtiene el número de semana epidemiológica dada una fecha, según la definición del Ministerio de Salud.
def numeroSemanaEpidemiologica(fecha):
    partesFecha = fecha.split('-')
    fechaIso = date(int(partesFecha[0]), int(partesFecha[1]), int(partesFecha[2]))
    semanaActual = fechaIso.isocalendar()[1]
    # La semana epidemiológica es la siguiente de la semana ISO, si el día es domingo.
    if fechaIso.weekday() == 6:
        semanaActual = semanaActual + 1
    return semanaActual - 1

# Suma los casos de una semana epidemiológica dada, para un distrito y un dataframe dados.
def sumarCasosSemana(distrito, semana, ano, df):
    # El offset es porque en esta columna empiezan las fechas
    COL_OFFSET = 6
    acumuladoSemana = 0
    sumo = False
    semanaCalculo = -1
    for col in range(COL_OFFSET, df.shape[1]):
        try:
            fecha = str(df.iloc[0, col]).split(' ')[0]
            
            # Si la fecha analizada pertenece a la semana epidemiológica requerida en el año especificado, se agrega el dato a la suma.
            if numeroSemanaEpidemiologica(fecha) == semana and (ano == fecha.split('-')[0] or ano == str(int(fecha.split('-')[0]) + 1)):
                if semanaCalculo == -1:
                    semanaCalculo = semana
                    sumo = True
                try:
                    acumuladoSemana += df.iloc[distrito, col] if df.iloc[distrito, col] >= 0 else 0
                except:
                    pass
            # Si ya cambió de semana epidemiológica después de sumar los casos, retorna
            elif numeroSemanaEpidemiologica(fecha) != semanaCalculo and sumo == True:
                return acumuladoSemana
        except Exception as e:
            consoleLog("Error!! " + str(e)  +" Columna: " + str(col) + "Distrito: " + str(distrito) + " Fecha: " + str(fecha))
            raise
    return acumuladoSemana
        
# Carga las alertas y las predicciones para cada distrito
def cargarEscenarios(filename):
    df = pd.read_excel(filename, header=0, sheet_name="PCD Escenarios")
    conn = getAuthConnection()
    cursor = conn.cursor()
    for row in range(1, df.shape[0]) : 
        prediccion = df.iloc[row, 7]
        semana = prediccion.split(' ')[0]
        mes = prediccion.split(' ')[2] if len(prediccion.split(' ')) > 2 else prediccion.split(' ')[1]
        #se carga el grupo y el nivel de alerta para todo el mes para cada distrito con los datos de la semana I por defecto
        if semana == 'I':
            
            # en caso de que no venga el Índice Socio Sanitario, no se pone la columna grupo en el query
            if df.iloc[row, 6] is np.nan:
                queryGrupo = """
                    UPDATE acumulado_distrito
                    SET condicion = '{condicion}'
                    WHERE codigo_distrito = '{distrito}'
                    AND date_part('month', fecha) = {mesActual}
                    AND fecha > '2020-12-31'
                """

                cursor.execute(queryGrupo.format(
                    distrito = df.iloc[row, 0],
                    condicion = df.iloc[row, 8],
                    mesActual = getNumeroMes(mes)
                ))

            else:
                queryGrupo = """
                    UPDATE acumulado_distrito
                    SET grupo = '{grupo}',
                    condicion = '{condicion}'
                    WHERE codigo_distrito = '{distrito}'
                    AND date_part('month', fecha) = {mesActual}
                    AND fecha > '2020-12-31'
                """

                cursor.execute(queryGrupo.format(
                    distrito = df.iloc[row, 0], 
                    grupo = df.iloc[row, 6],
                    condicion = df.iloc[row, 8],
                    mesActual = getNumeroMes(mes)
                ))

        queryPrediccion = """
            INSERT INTO prediccion_distrito (
                codigo_distrito,
                nombre_distrito,
                mes,
                semana,
                activos,
                prevalencia,
                acumulado,
                inv_acum
            )
            VALUES (
                '{codigo_distrito}',
                '{nombre_distrito}',
                {mes},
                '{semana}',
                {activos},
                {prevalencia},
                {acumulado},
                {inv_acum}
            ) ON CONFLICT DO NOTHING;
                """

        activos = df.iloc[row, 2]
        prevalencia = df.iloc[row, 3]
        acumulado = df.iloc[row, 4]
        inv_acum = df.iloc[row, 5]

        if np.isnan(activos):
            activos = 0
        if np.isnan(prevalencia):
            prevalencia = 0
        if np.isnan(acumulado):
            acumulado = 0
        if np.isnan(inv_acum):
            inv_acum = 0

        cursor.execute(queryPrediccion.format(
            codigo_distrito = df.iloc[row, 0],
            nombre_distrito = df.iloc[row, 1],
            mes = getNumeroMes(mes),
            semana = semana,
            activos = activos,
            prevalencia = prevalencia,
            acumulado = acumulado,
            inv_acum = inv_acum
        ))
        consoleLog  ("-----------------------")
        consoleLog (df.iloc[row, 1])
        consoleLog  ("-----------------------")
        conn.commit()  
    closeConnection(conn)

# Carga los datos de población para cada distrito, solo se usa una única vez para insertar los datos y no se actualiza.
def cargarDistritos():
    df = pd.read_excel("COVID19CR.xlsx", header= None, sheet_name="PoblacionDistrito")
    conn = getAuthConnection()
    cursor = conn.cursor()
    for row in range(1, df.shape[0]):
        query = """
            INSERT INTO datos_distrito
            VALUES ('{codigo_distrito}', {poblacion}, {pob_am}, {pob_pobre})
        """
        cursor.execute(query.format(
            codigo_distrito = df.iloc[row, 0].split(':')[0],
            poblacion = df.iloc[row, 7],
            pob_am = round((df.iloc[row, 6] / df.iloc[row, 7]) * 100, 2),
            pob_pobre = 0.0
        ))
        conn.commit()
    closeConnection(conn)

def cargarDenuncias(fecha):
    url = 'https://apicovid.estuve-aqui.com/integrations/v1/ucr/sanitaryorders/details?limitDate=' + str(fecha)
    head = {"ucr-token" : "ib41jDxofoRccn73Z79Kkts6YCCvfPxW8axklf0AKNeJ69ouem8ubymBpsqzHNC3YrZoPgiU9MKOAFKGZhJkbBxqG9q2ShG4I9IbCS6qRYu9TH"} 
    r = requests.get(url,headers=head)
    df = pd.read_json( r.content )
    consoleLog('Cargando denuncias en la fecha: ' + str(fecha))
    if len(df) > 0:
        pd.options.display.max_colwidth = 500
        query = "SELECT DISTINCT codigo, nom_prov, nom_cant, nom_dist from distrito"
        conn = getAuthConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            suma = 0
            for district in df['data']:
                if district['state'] == row[1] and district['city'] == row[2] and district['district'] == row[3]:
                    suma += int(district['total'])
            insert_query = """
                INSERT INTO ordenes_fecha
                VALUES ('{fecha}', '{codigo_distrito}', {denuncias})
                ON CONFLICT DO NOTHING;
            """
            cursor.execute(insert_query.format(
                fecha = fecha,
                codigo_distrito = str(row[0]),
                denuncias = suma
            ))
            conn.commit()
            consoleLog('Cargando denuncias para distrito: ' + str(row[0]))
        closeConnection(conn)

def validateDate(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        return False
    return True

def getLastDate():
    conn = getAuthConnection()
    cursor = conn.cursor()
    query = "select fecha from acumulado_distrito ad order by fecha desc limit 1"
    cursor.execute(query)
    return cursor.fetchone()

def getNumeroMes(mes):
    if mes == 'Ene' or mes == 'Enero':
        return 1
    elif mes == 'Feb' or mes == 'Febrero':
        return 2
    elif mes == 'Mar' or mes == 'Marzo':
        return 3
    elif mes == 'Abr' or mes == 'Abril':
        return 4
    elif mes == 'May' or mes == 'Mayo':
        return 5
    elif mes == 'Jun' or mes == 'Junio':
        return 6
    elif mes == 'Jul' or mes == 'Julio':
        return 7
    elif mes == 'Ago' or mes == 'Agosto':
        return 8
    elif mes == 'Sep' or mes == 'Septiembre':
        return 9
    elif mes == 'Oct' or mes == 'Octubre':
        return 10
    elif mes == 'Nov' or mes == 'Noviembre':
        return 11
    elif mes == 'Dic' or mes == 'Diciembre':
        return 12
    else:
        return -1

def main(argv):
    if len(argv) < 1:
        consoleLog("Uso: carga_datos.py <Archivo COVID19> <Archivo escenarios>")
        return False
    else:
        if len(argv) >= 1:
            try:
                archivoCovid = argv[0]
                archivoEscenarios = argv[1]
                cargarDatos(archivoCovid, archivoEscenarios)
            except Exception as e:
                consoleLog("No se pudo cargar datos. Error: " + str(e))
                raise
                return False
        return True

# Carga todos los datos de actualización regular a partir de dos archivos. Esta función es llamada desde el cron job que la ejecuta para actualizar automáticamente.
def cargarDatos(archivoCovid, archivoEscenarios):
    print("Inicio de carga: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    try:
        ultimaFecha = getLastDate()[0].strftime('%Y-%m-%d')
        consoleLog("Ultima fecha en la BD: " + str(ultimaFecha))
        cargarCasos(archivoCovid, ultimaFecha)
        archivoCasosDiarios = pd.read_excel(archivoCovid, header= None, sheet_name="DistritosNuevos")
        cargarCasosDiarios(archivoCasosDiarios, ultimaFecha)
        cargarDatosPais(archivoCovid, ultimaFecha)
        cargarCoefVar(archivoCovid, ultimaFecha)
        cargarEscenarios(archivoEscenarios)
        # cargarCapasProyecciones()
    except Exception as e:
        consoleLog("Ha ocurrido un error al cargar los datos: " + str(e))
        noti = Notificador()
        noti.notificar(str(e))

    print("Fin de carga: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# Carga la tasa de morbilidad por distrito. Solo se utiliza una vez y no se actualiza.
def cargarMorbilidad():
    consoleLog("Leyendo archivo de datos...")
    df = pd.read_excel("Morbilidad.xlsx", header= None, sheet_name="Base Final", usecols="C,M")
    consoleLog("archivo de datos leído")
    try:
        conn = getAuthConnection()
        cursor = conn.cursor()
        for row in range(1, df.shape[0]) : 
            distrito = df.iloc[row, 0]
            morbilidad = df.iloc[row, 1]
            consoleLog (distrito)
            q = """
                    INSERT INTO morbilidad_distrito (codigo_distrito, morbilidad)
                    VALUES ({codigo}, {morbilidad})"""
            query = q.format(
                codigo = distrito,
                morbilidad = morbilidad
            )
            if not np.isnan(morbilidad):    
                cursor.execute(query)
            consoleLog  ("-----------------------")
            conn.commit()  
    except (Exception, psql.Error) as error:
        consoleLog("Error while connecting to PostgreSQL" + error)
        raise
            
    closeConnection(conn)

# Carga los datos de hospitalizaciones en salón y UCI, y el índice de positividad, a nivel país. Se actualiza regularmente.
def cargarDatosPais(archivo, ultimaFecha):
    df = pd.read_excel(archivo, header= None, sheet_name="Datos", usecols="B,C,AG,AI,AY")
    try:
        conn = getAuthConnection()
        cursor = conn.cursor()
        for row in range(1, df.shape[0]) : 
            fecha = str(df.iloc[row, 0]).split(' ')[0]
            if fecha > ultimaFecha or DEBUG == True:
                consoleLog("Cargando datos país para la fecha: " + str(fecha))
                acumulados = df.iloc[row, 1]
                casos_salon = df.iloc[row, 2]
                casos_uci = df.iloc[row, 3]
                muestras = df.iloc[row, 4]
                indice_positividad = 0
                try:
                    indice_positividad = (acumulados / muestras) * 100
                except Exception as e:
                    consoleLog(str(e))
                if np.isnan(indice_positividad):
                    indice_positividad = 'null'
                else:
                    indice_positividad = round(indice_positividad, 2)
                q = """
                        INSERT INTO datos_pais (fecha, casos_salon, casos_uci, indice_positividad)
                        VALUES ('{fecha}', {casos_salon}, {casos_uci}, {indice_positividad}) ON CONFLICT DO NOTHING;"""
                if not np.isnan(casos_salon) and not np.isnan(casos_uci):
                    query = q.format(
                        fecha = fecha,
                        casos_salon = casos_salon,
                        casos_uci = casos_uci,
                        indice_positividad = indice_positividad
                    )
                    cursor.execute(query)
                    consoleLog  ("-----------------------")
                    conn.commit()
    except (Exception, psql.Error) as error :
        consoleLog("Error cargando los datos país: " + str(error))
        raise
            
    closeConnection(conn)

def cargarCapasProyecciones():
    df = gpd.read_file('50 Dist 20 al 26 Jun.geojson', ignore_geometry=True)

    try:
        conn = getAuthConnection()
        cursor = conn.cursor()
        for row in range(len(df)):
            queryGrupo = """
                    INSERT INTO proyeccion_distrito (codigo_dta, porcentaje, fecha_inicio, fecha_fin, muestra)
                    VALUES ({codigo_dta}, {porcentaje}, '{fecha_inicio}', '{fecha_fin}', {muestra}) ON CONFLICT DO NOTHING;
                """

            cursor.execute(queryGrupo.format(
                codigo_dta = df.iloc[row]['codigo_dta'],
                porcentaje = df.iloc[row, -1],
                fecha_inicio = '2021-06-20',
                fecha_fin = '2021-06-26',
                muestra= 50
            ))

            conn.commit()
        closeConnection(conn)

    except Exception as e:
        consoleLog("Ha ocurrido un error al cargar los datos: " + str(e))
        raise

if __name__ == "__main__":
    if not main(sys.argv[1:]):
        sys.exit(1)
    else:
        sys.exit(0)
