from mapa.libreria.bd import getAuthConnection, closeConnection
import geopandas as gpd


def getCantones(provincia):
    """
    Obtiene la lista de nombres de cantones de una provincia dada.

    Parámetros
    ----------
    provincia : str
        Nombre de la provincia cuyos cantones se quieren obtener.

    Retorna
    -------
    list
        Lista que contiene el nombre de los cantones de la provincia dada.
    """

    conn = getAuthConnection()
    cursor = conn.cursor()
    getCantonesQuery = """
        select c.nom_cant_1 from canton c where UNACCENT(nom_prov) ILIKE UNACCENT('{provincia}') order by nom_cant_1
    """

    cursor.execute(getCantonesQuery.format(provincia=provincia))
    records = cursor.fetchall()

    cantones = []

    for row in records:
        cantones.append(row[0])

    closeConnection(conn)

    return cantones


def getDistritos(canton):
    """
    Obtiene la lista de nombres de distritos de un cantón dado.

    Parámetros
    ----------
    canton : str
        Nombre del cantón cuyos distritos se quieren obtener.

    Retorna
    -------
    list
        Lista que contiene el nombre de los distritos del cantón dado.
    """

    conn = getAuthConnection()
    cursor = conn.cursor()
    getDistritosQuery = """
        select distinct d.nom_dist from distrito d where UNACCENT(nom_cant) ILIKE UNACCENT('{canton}') order by nom_dist
    """

    cursor.execute(getDistritosQuery.format(canton=canton))
    records = cursor.fetchall()

    distritos = []

    for row in records:
        distritos.append(row[0])

    closeConnection(conn)

    return distritos


def getFechasValidas():
    """
    Obtiene todas las fechas registradas en la tabla acumulado_distrito, es decir, son las fechas para las cuales hay datos.

    Retorna
    -------
    list
        Lista que contiene todas las fechas válidas de la base de datos, en orden descendente.
    """

    conn = getAuthConnection()
    cursor = conn.cursor()
    getFechasQuery = """
        select distinct fecha from acumulado_distrito order by fecha desc
    """

    cursor.execute(getFechasQuery)
    records = cursor.fetchall()

    fechas = []

    for row in records:
        fechas.append(row[0])

    closeConnection(conn)

    return fechas


def getQueryNacional():
    """
    Crea la consulta para obtener la cantidad de casos acumulados, recuperados, activos y casos nuevos por fecha, para todo el país.

    Retorna
    -------
    str
        Consulta que retorna la cantidad de casos acumulados, recuperados, activos y casos nuevos por fecha, para todo el país.
    """

    query = """
        select fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum(activos) as activos, sum(caso_dia) as caso_dia
        from acumulado_distrito
        group by fecha order by fecha asc;
    """
    return query


def getQueryOrdenesPers(fecha):
    """
    Crea la consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, a nivel nacional.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos de la consulta.

    Retorna
    -------
    str
        Consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha.
    """

    if fecha != None:
        query = """
            select sum(denuncias_personas) as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' 
        """
        return query.format(fecha=fecha)
    else:
        query = """
            select sum(denuncias_personas) as pers, 0 as den, fecha from ordenes_fecha group by fecha order by fecha asc
        """
        return query


def getQueryOrdenesPersProv(fecha, provincia):
    """
    Crea la consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, para una provincia dada.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos de la consulta.
    provincia : str
        Nombre de la provincia para la que se desea obtener los datos de la consulta.

    Retorna
    -------
    str
        Consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, para una provincia dada.
    """

    if fecha != None:
        query = """
            select sum(denuncias_personas) as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' and
            substring( cod_distrito::varchar, 1,1 ) = ( select substring( codigo::varchar, 1,1 )
            from distrito d where LOWER( d.nom_prov ) = LOWER('{provincia}') limit 1);
        """
        return query.format(fecha=fecha, provincia=provincia)
    else:
        query = """
            select sum(denuncias_personas) as pers, 0 as den, fecha from ordenes_fecha
            where substring( cod_distrito::varchar, 1,1 ) = ( select substring( codigo::varchar, 1,1 )
            from distrito d where LOWER( d.nom_prov ) = LOWER('{provincia}') limit 1) group by fecha order by fecha asc;
        """
        return query.format(provincia=provincia)


def getQueryOrdenesPersCanton(fecha, provincia, canton):
    """
    Crea la consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, para un cantón dado.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos de la consulta.
    provincia : str
        Nombre de la provincia para la que se desea obtener los datos de la consulta.
    canton : str
        Nombre del cantón para el cual se desea obtener los datos de la consulta.

    Retorna
    -------
    str
        Consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, para un cantón dado.
    """

    if fecha != None:
        query = """
            select sum(denuncias_personas) as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' and
            substring( cod_distrito::varchar, 1,3 ) = ( select substring( codigo::varchar, 1,3 )
            from distrito d where UNACCENT( d.nom_prov ) ILIKE UNACCENT('{provincia}') and UNACCENT ( d.nom_cant ) ILIKE UNACCENT ('{canton}') limit 1);
        """
        return query.format(fecha=fecha, provincia=provincia, canton=canton)
    else:
        query = """
            select sum(denuncias_personas) as pers, 0 as den, fecha from ordenes_fecha
            where substring( cod_distrito::varchar, 1,3 ) = ( select substring( codigo::varchar, 1,3 )
            from distrito d where UNACCENT( d.nom_prov ) ILIKE UNACCENT('{provincia}') and UNACCENT ( d.nom_cant ) ILIKE UNACCENT ('{canton}') limit 1) group by fecha order by fecha asc;
        """
        return query.format(provincia=provincia, canton=canton)


def getQueryOrdenesPersDist(fecha, provincia, canton, distrito):
    """
    Crea la consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, para un distrito dado.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos de la consulta.
    provincia : str
        Nombre de la provincia para la que se desea obtener los datos de la consulta.
    canton : str
        Nombre del cantón para el cual se desea obtener los datos de la consulta.
    distrito : str
        Nombre del distrito para el cual se desea obtener los datos de la consulta.

    Retorna
    -------
    str
        Consulta para obtener la suma de órdenes sanitarias a personas, en total o agrupada por fecha, para un distrito dado.
    """

    if fecha != None:
        query = """
            select denuncias_personas as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' and
            cod_distrito = ( select codigo
            from distrito d where UNACCENT( d.nom_dist ) ILIKE UNACCENT('{distrito}') and UNACCENT(d.nom_cant) ILIKE UNACCENT('{canton}') and UNACCENT(d.nom_prov) ILIKE UNACCENT('{provincia}') LIMIT 1)
        """
        return query.format(
            fecha=fecha, distrito=distrito, canton=canton, provincia=provincia
        )
    else:
        query = """
            select denuncias_personas as pers, 0 as den, fecha from ordenes_fecha
            where cod_distrito = ( select codigo
            from distrito d where UNACCENT( d.nom_dist ) ILIKE UNACCENT('{distrito}') and UNACCENT(d.nom_cant) ILIKE UNACCENT('{canton}') and UNACCENT(d.nom_prov) ILIKE UNACCENT('{provincia}') LIMIT 1) order by fecha asc
        """
        return query.format(distrito=distrito, canton=canton, provincia=provincia)


def get_sedes():
    """
    Obtiene la capa de sedes de examen de admisión para el proces de 2020-2021, representados como puntos en el mapa, cada uno con su respectivo nombre.

    Retorna
    -------
    Geojson
        Capa de sedes de examen de admisión para el proces de 2020-2021, representados como puntos en el mapa, con su respectivo nombre.

    """

    query = """
        select wkb_geometry, nombre, total from sede_examen_adminsion
    """

    conn = getAuthConnection()

    df = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="wkb_geometry")
    gjson = df.to_crs(epsg="4326").to_json()

    closeConnection(conn)

    return gjson


def get_hogares():
    """
    Obtiene la capa de hogares de ancianos en Costa Rica, representados como puntos en el mapa, cada uno con su respectivo nombre.

    Retorna
    -------
    Geojson
        Capa de hogares de ancianos en Costa Rica, representados como puntos en el mapa, cada uno con su respectivo nombre.

    """

    query = """
        select wkb_geometry, nombre from hogar
    """

    conn = getAuthConnection()

    df = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="wkb_geometry")
    gjson = df.to_crs(epsg="4326").to_json()

    closeConnection(conn)

    return gjson


def get_indigenas():
    """
    Obtiene la capa de asentamientos indígenas de Costa Rica, representados como áreas naranjas en el mapa, cada una con su respectivo nombre.

    Retorna
    -------
    Geojson
        Capa de asentamientos indígenas de Costa Rica, representados como áreas naranjas en el mapa, cada una con su respectivo nombre.

    """

    query = """
        select wkb_geometry, pueblo from terr_indigena
    """

    conn = getAuthConnection()

    df = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="wkb_geometry")
    df.crs = "EPSG:4326"
    gjson = df.to_crs(epsg="4326").to_json()

    closeConnection(conn)

    return gjson


def get_dist(fecha):
    """
    Obtiene las capas que componen el mapa que son los distritos con todos sus metadatos: casos activos, casos acumulados, casos fallecidos, casos recuperados, casos nuevos,
    pendiente, tasa de ataque, coeficiente de variación, índice socio sanitario, denuncias al 911, tasa de morbilidad, cantidad de población total, cantidad de población
    adulta mayor, porcentaje de pobreza, nombre del distrito, nombre del cantón y nombre de provincia, todo esto para cada distrito para una fecha dada.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener las capas del mapa.

    Retorna
    -------
    Geojson
        Capa principal del mapa con todos los metadatos incluidos en la geometría de cada distrito, para una fecha dada.
    """

    query = """
        select distinct ST_SimplifyPreserveTopology( d.wkb_geometry, 0.001 ) as wkb_geometry, d.codigo_distr as codigo, d.nom_dist as nombre, d.nom_prov as proInfo, nom_cant as cantInfo,
        p.poblacion as pobInfo, p.pob_pobre as pobPobre, p.pob_am as pobAm, count(den.consecutivo) as denuncias,
        m.morbilidad as morbilidad,
        ( select cantidad as activos from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select ta from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select pendiente from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select fallecidos from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select recuperados from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select coef_var || '%' as coef_var from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select grupo as socio from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select condicion from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select caso_dia from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}')
        from distrito d join datos_distrito p on d.codigo_distr = p.codigo_distrito
        join morbilidad_distrito m on d.codigo_distr = m.codigo_distrito
        left outer join denuncia_911 den on den.cod_dist = d.codigo_distr and fecha = '{fecha}'
        group by d.wkb_geometry, d.codigo_distr, d.nom_dist, d.nom_prov, nom_cant, p.poblacion, p.pob_pobre, p.pob_am, m.morbilidad
        order by d.codigo_distr
    """

    conn = getAuthConnection()

    df = gpd.GeoDataFrame.from_postgis(
        query.format(fecha=fecha), conn, geom_col="wkb_geometry"
    )
    df.crs = "EPSG:4326"
    df["fillColor"] = "red"
    gjson = df.to_crs(epsg="4326").to_json()

    closeConnection(conn)

    return gjson


def getLastDate():
    """
    Obtiene la fecha más reciente registrada para la que se conocen datos en la base de datos.

    Retorna
    -------
    str
        Fecha más reciente registrada en la tabla acumulado_distrito, en el formato YYYY-MM-DD.
    """

    conn = getAuthConnection()
    cursor = conn.cursor()
    query = "select fecha from acumulado_distrito ad order by fecha desc limit 1"
    cursor.execute(query)

    result = cursor.fetchone()
    closeConnection(conn)
    return result


def obtenerDatosPais(fecha):
    """
    Obtiene los datos a nivel país de hospitalizaciones en salón, hospitalizaciones en UCI e índice de positividad registrados en una fecha dada.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desean obtener los datos.

    Retorna
    -------
    dict
        Diccionario que contiene los datos a nivel país de hospitalizaciones en salón, hospitalizaciones en UCI e índice de positividad registrados en una fecha dada.
    """
    if fecha:
        query = """
            select casos_salon, casos_uci, indice_positividad from datos_pais where fecha = '{fecha}';
        """
    else:
        query = """
            select casos_salon, casos_uci, indice_positividad from datos_pais order by fecha desc limit 1;
        """

    conn = getAuthConnection()
    cursor = conn.cursor()

    if fecha:
        cursor.execute(query.format(fecha=fecha))
    else:
        cursor.execute(query)

    records = cursor.fetchall()

    datos = {}

    datos["casos_salon"] = records[0][0]
    datos["casos_uci"] = records[0][1]
    datos["indice_positividad"] = str(records[0][2]) + "%"
    closeConnection(conn)
    return datos


def getPredicciones(mes, semana, ano):
    """
    Obtiene las predicciones de casos activos por distrito para un mes y semana de predicción dados.

    Parámetros
    ----------
    mes : int
        Número de mes de 1 a 12 para el cual se desea obtener las predicciones.
    semana : str
        Semana (I, II, III, IV, V) para la cual se desea obtener las predicciones según el mes dado.
    ano : int
        Año para el cual se desea obtener las predicciones.

    Retorna
    -------
    dict
        Diccionario que contiene las predicciones consultadas para el mes y semana dados.
    """

    query = """
        SELECT codigo_distrito, activos, grupo as socio from prediccion_distrito WHERE mes = {mes} and semana = '{semana}' and ano = {ano}
    """

    conn = getAuthConnection()
    cursor = conn.cursor()

    cursor.execute(query.format(mes=mes, semana=semana, ano=ano))
    records = cursor.fetchall()

    datos = {}

    for row in records:
        tupla = {}
        tupla["activos"] = row[1]
        tupla["socio"] = row[2]
        datos[str(row[0])] = tupla
    closeConnection(conn)
    return datos


def obtenerProyecciones(fecha, muestra):
    """
    Obtiene los datos de proyecciones para muestras determinadas de distritos, para una fecha que caiga en el rango de una proyección registrada en la base de datos.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos de proyecciones para muestras determinadas de distritos.
    muestra : int
        Tamaño predeterminado de la muestra en la base de datos: 15, 20, 40 o 50.

    Retorna
    -------
    dict
        Diccionario que contiene los datos de proyecciones para muestras determinadas de distritos, para una fecha que caiga en el rango de una proyección registrada en la base de datos.
    """

    query = """
        SELECT codigo_dta, porcentaje, muestra from proyeccion_distrito WHERE fecha_inicio <= '{fecha}' and fecha_fin > '{fecha}' and muestra = {muestra}
    """

    conn = getAuthConnection()
    cursor = conn.cursor()

    cursor.execute(query.format(fecha=fecha, muestra=muestra))
    records = cursor.fetchall()

    datos = {}

    for row in records:
        tupla = {}
        tupla["porcentaje"] = row[1]
        tupla["muestra"] = row[2]
        datos[str(row[0])] = tupla
    closeConnection(conn)
    return datos


def getQueryVacunas(fecha):
    """
    Obtiene los datos de primeras dosis aplicadas y segundas dosis aplicadas para una fecha dada, a nivel país.
    Este método retorna datos cuando la fecha dada coincide con alguna fecha donde existen datos de vacunación registrados en la base de datos.
    Si no hay datos para la fecha dada, se debe usar getQueryVacunasDefault().

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos de vacunación.

    Retorna
    -------
    str
        Consulta que obtiene los datos de primeras dosis aplicadas y segundas dosis aplicadas para una fecha dada, a nivel país.
    """

    query = """
        SELECT vacunas_primera_dosis, vacunas_segunda_dosis, vacunas_primera_dosis + vacunas_segunda_dosis as total_vacunas, to_char(fecha, 'DD-MM-YYYY') FROM datos_pais WHERE fecha = '{fecha}' and vacunas_primera_dosis is not null
    """
    return query.format(fecha=fecha)


def getQueryVacunasDefault():
    """
    Obtiene los datos de primeras dosis aplicadas y segundas dosis aplicadas en la última fecha en la que hayan datos de vacunación registrados en la base de datos, a nivel país.

    Retorna
    -------
    str
        Consulta que obtiene los datos de primeras dosis aplicadas y segundas dosis aplicadas en la última fecha de la que se tengan datos de vacunación en la base de datos, a nivel país.
    """

    query = """
        SELECT vacunas_primera_dosis, vacunas_segunda_dosis, vacunas_primera_dosis + vacunas_segunda_dosis AS total_vacunas, to_char(fecha, 'DD-MM-YYYY') FROM datos_pais WHERE vacunas_primera_dosis IS NOT NULL ORDER BY fecha DESC LIMIT 1
    """
    return query
