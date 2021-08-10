import psycopg2 as psql
from mapa.libreria.bd import getMyConnection
import geopandas as gpd

conn = getMyConnection()

def getCantones(provincia):
    conn = getMyConnection()
    cursor = conn.cursor()
    getCantonesQuery = """
        select c.nom_cant_1 from canton c where UNACCENT(nom_prov) ILIKE UNACCENT('{provincia}') order by nom_cant_1
    """

    cursor.execute( getCantonesQuery.format(provincia = provincia) )
    records = cursor.fetchall()

    cantones = []
 
    for row in records:
        cantones.append(row[0])

    return cantones

def getDistritos(canton):
    conn = getMyConnection()
    cursor = conn.cursor()
    getDistritosQuery = """
        select distinct d.nom_dist from distrito d where UNACCENT(nom_cant) ILIKE UNACCENT('{canton}') order by nom_dist
    """

    cursor.execute( getDistritosQuery.format(canton = canton))
    records = cursor.fetchall()

    distritos = []
 
    for row in records:
        distritos.append(row[0])

    return distritos

def getFechasValidas():
    conn = getMyConnection()
    cursor = conn.cursor()
    getFechasQuery = """
        select distinct fecha from acumulado_distrito order by fecha desc
    """

    cursor.execute(getFechasQuery)
    records = cursor.fetchall()

    fechas = []
 
    for row in records:
        fechas.append(row[0])

    return fechas

#Retorna la cantidad de casos acumulados, recuperados y activos para una provincia dada
def getQueryProvincia( nombre ):
    query = """
    select  fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum( activos) as activos, sum(caso_dia) as caso_dia
    from ( select distinct id, nom_prov, nom_cant, nom_dist as distrito from distrito ) as d, acumulado_distrito a
    where a.codigo_distrito = d.id
	and d.nom_prov = '{province}'
    group by fecha order by fecha asc;"""
    
    return query.format(province = nombre)

# Obtiene la cantidad de casos acumulados, activos, recuperados y 
def getQueryDistrito(provincia, canton, distrito):
    query = """
    select  fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum( activos) as activos, sum(caso_dia) as caso_dia
    from ( select distinct id, nom_prov, nom_cant, nom_dist as distrito from distrito ) as d, acumulado_distrito a
    where a.codigo_distrito = d.id
	and d.nom_prov = '{province}'
    and d.nom_cant = '{canton}'
    and d.nom_dist = '{distrito}'
    group by fecha order by fecha asc;"""
    return query.format(province = provincia, canton = canton, distrito = distrito)


# ? PREGUNTAR, no tenemos datos de coef_var ni pendiente
# * se va a usar incidence_rate en vez de coef_var, pendiente puede ser crecimiento, ta es tasa de ataque
def getQueryAcumuladosFecha( fecha ):
    query = """
        select d.id, d.nom_dist, d.nom_cant, d.nom_prov,
        ad.cantidad, ad.recuperados, ad.fallecidos, ad.activos, ad.ta, ad.coef_var, ad.pendiente, 
            case when ad.condicion = 'Naranja'  then '#ffbe61' 
                 when ad.condicion = 'Amarillo' then '#ffff00' end
        from distrito d left join acumulado_distrito ad on ad.codigo_distrito = d.id
        where fecha = '{date}'
        order by ad.cantidad desc;
    """
    return query.format(date = fecha)

# !No migrar, está sobre distrito
def getQueryProvinceMap( province, fecha ):
    query = """
    select  *, 
        ( select cantidad 
          from acumulado_distrito 
          where fecha = '{date}' 
          and  codigo_distrito = d.id
        ) 
    from distrito d 
    where d.nom_prov = '{provincia}'
    order by cantidad asc;"""
    return query.format(date = fecha, provincia = province)

def getMaxCasosProvinciaFecha(date):
    query = """
    select max(sum) from (
        select sum(ad.cantidad), d.nom_prov from acumulado_distrito ad join distrito d on ad.codigo_distrito = d.id
        where fecha = '{fecha}'
        group by d.nom_prov
	) acumulados
    """
    return query.format(fecha = date)

#PENDIENTE
def getCasosProvinciaFecha(columna, fecha, provincia):
    query = """
        select sum(ad.{col}), provincia from acumulado_distrito ad join distrito d on ad.codigo_distrito = d.id
        where fecha = '{date}'
        and provincia = '{province}'
        group by provincia
    """
    return query.format(col = columna, date = fecha, province = provincia)

	
def getQueryNacional():
    query = """
    select  fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum( activos) as activos, sum(caso_dia) as caso_dia
    from ( select distinct codigo_distr, nom_prov, nom_cant, nom_dist as distrito from distrito ) as d, acumulado_distrito a
    where a.codigo_distrito = d.codigo_distr
    group by fecha order by fecha asc;"""
    return query

def getQueryRt( fecha ):
    query = """
    select  * from rt_semanal
    order by semana asc;"""
    return query

def getQueryUCIOptimista():
    query = """
    select 	fecha, conac_hospi, conac_uci from  proyeccion_hosp;
    """
    return query

def getQueryUCIPesimista():
    query = """
    select 	fecha, sinac_hospi, sinac_uci  from  proyeccion_hosp;
    """
    return query 

	
def getQueryOrdenesPers(fecha):
    if fecha != None:
        query = """
            select sum(denuncias_personas) as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' 
        """
        return query.format(fecha = fecha)
    else:
        query = """
            select sum(denuncias_personas) as pers, 0 as den, fecha from ordenes_fecha group by fecha order by fecha asc
        """
        return query

def getQueryOrdenesPersProv(fecha, provincia):
    if fecha != None:
        query = """
            select sum(denuncias_personas) as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' and
            substring( cod_distrito::varchar, 1,1 ) = ( select substring( codigo::varchar, 1,1 )
            from distrito d where LOWER( d.nom_prov ) = LOWER('{provincia}') limit 1);
        """
        return query.format(fecha = fecha, provincia = provincia)
    else:
        query = """
            select sum(denuncias_personas) as pers, 0 as den, fecha from ordenes_fecha
            where substring( cod_distrito::varchar, 1,1 ) = ( select substring( codigo::varchar, 1,1 )
            from distrito d where LOWER( d.nom_prov ) = LOWER('{provincia}') limit 1) group by fecha order by fecha asc;
        """
        return query.format(provincia = provincia)

def getQueryOrdenesPersCanton(fecha, provincia, canton):
    if fecha != None:
        query = """
            select sum(denuncias_personas) as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' and
            substring( cod_distrito::varchar, 1,3 ) = ( select substring( codigo::varchar, 1,3 )
            from distrito d where UNACCENT( d.nom_prov ) ILIKE UNACCENT('{provincia}') and UNACCENT ( d.nom_cant ) ILIKE UNACCENT ('{canton}') limit 1);
        """
        return query.format(fecha = fecha, provincia = provincia, canton = canton)
    else:
        query = """
            select sum(denuncias_personas) as pers, 0 as den, fecha from ordenes_fecha
            where substring( cod_distrito::varchar, 1,3 ) = ( select substring( codigo::varchar, 1,3 )
            from distrito d where UNACCENT( d.nom_prov ) ILIKE UNACCENT('{provincia}') and UNACCENT ( d.nom_cant ) ILIKE UNACCENT ('{canton}') limit 1) group by fecha order by fecha asc;
        """
        return query.format(provincia = provincia, canton = canton)

def getQueryOrdenesPersDist(fecha, provincia, canton, distrito):
    if fecha != None:
        query = """
            select denuncias_personas as pers, 0 as den from ordenes_fecha
            where fecha = '{fecha}' and
            cod_distrito = ( select codigo
            from distrito d where UNACCENT( d.nom_dist ) ILIKE UNACCENT('{distrito}') and UNACCENT(d.nom_cant) ILIKE UNACCENT('{canton}') and UNACCENT(d.nom_prov) ILIKE UNACCENT('{provincia}') LIMIT 1)
        """
        return query.format(fecha = fecha, distrito = distrito, canton = canton, provincia = provincia)
    else:
        query = """
            select denuncias_personas as pers, 0 as den, fecha from ordenes_fecha
            where cod_distrito = ( select codigo
            from distrito d where UNACCENT( d.nom_dist ) ILIKE UNACCENT('{distrito}') and UNACCENT(d.nom_cant) ILIKE UNACCENT('{canton}') and UNACCENT(d.nom_prov) ILIKE UNACCENT('{provincia}') LIMIT 1) order by fecha asc
        """
        return query.format(distrito = distrito, canton = canton, provincia = provincia)
	
#--------------------------------------------------------------------------

def getQueryOrdenesEstProv( provincia ):
    query = """
	select 	sum(cant_ord_est) as est, sum(cant_den_est) as den  from  ordenes_est where substring( codigo::varchar, 1,1 ) = ( select fid::varchar from provincia p where LOWER( p.nprovincia ) = LOWER('{province}')  ); 
    """
    return query.format(province = provincia) 

def getQueryOrdenesEst(  ):
    query = """
	select 	sum(cant_ord_est) as est, sum(cant_den_est) as den  from  ordenes_est;
    """
    return query 

def getQueryOrdenesEstDist( provincia, canton, distrito ):
    query = """
	select 	sum(cant_ord_est) as est, sum(cant_den_est) as den  from  ordenes_est;
    """
    return query 
	
def getQueryOrdenesEstCanton( provincia, canton ):
    query = """
	select 	sum(cant_ord_est) as est, sum(cant_den_est) as den  from  ordenes_est;
    """
    return query 
	

#Queries migrados de geom_creator

def get_leaflet_prov():
	query = """
		select p.wkb_geometry, p.nprovincia as nombre 
		from provincia p  ;
		"""
		
	df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
	gjson = df.to_crs(epsg='4326').to_json()

	return gjson #
	
def get_prov():
	query = """
		select p.wkb_geometry, p.nprovincia as nombre 
		from provincia p  ;
		"""
	df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
	gjson = df.to_crs(epsg='4326').to_json()

	return gjson 
	
def get_cant():
	query = """
		select c.wkb_geometry, c.nom_cant_1 as nombre
		from canton c;
		"""

	df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
	gjson = df.to_crs(epsg='4326').to_json()

	return gjson #

def get_sedes():
    query = """
        select wkb_geometry, nombre, total from sede_examen_adminsion
    """

    df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
    gjson = df.to_crs(epsg='4326').to_json()
    return gjson

def get_hogares():
    query = """
        select wkb_geometry, nombre from hogar
    """

    df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
    gjson = df.to_crs(epsg='4326').to_json()
    return gjson

def get_indigenas():
    query = """
        select wkb_geometry, pueblo from terr_indigena
    """

    df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
    df.crs = "EPSG:4326"
    gjson = df.to_crs(epsg='4326').to_json()
    return gjson

def get_dist(fecha):
    query = """
        select distinct ST_SimplifyPreserveTopology( d.wkb_geometry, 0.001 ) as wkb_geometry, d.codigo_distr as codigo, d.nom_dist as nombre, d.nom_prov as proInfo, nom_cant as cantInfo,
        p.poblacion as pobInfo, p.pob_pobre as pobPobre, p.pob_am as pobAm, count(den.consecutivo) as denuncias,
        m.morbilidad as morbilidad,
        ( select cantidad as activos from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select ta  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select pendiente from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select fallecidos from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select recuperados from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select coef_var || '%' as coef_var from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select grupo as socio   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select ids_salud  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select condicion   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
        ( select caso_dia from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}')
        from distrito d join datos_distrito p on d.codigo_distr = p.codigo_distrito
        join morbilidad_distrito m on d.codigo_distr = m.codigo_distrito
        left outer join denuncia_911 den on den.cod_dist = d.codigo_distr and fecha = '{fecha}'
        group by d.wkb_geometry, d.codigo_distr, d.nom_dist, d.nom_prov, nom_cant, p.poblacion, p.pob_pobre, p.pob_am, m.morbilidad
        order by d.codigo_distr
    """
    df = gpd.GeoDataFrame.from_postgis( query.format(fecha = fecha) , conn, geom_col='wkb_geometry')
    df.crs = 'EPSG:4326'
    df['fillColor'] = 'red'
    gjson = df.to_crs(epsg='4326').to_json()
    return gjson 
	
	
def getLastDate():
    conn = getMyConnection()
    cursor = conn.cursor()
    query = "select fecha from acumulado_distrito ad order by fecha desc limit 1"
    cursor.execute(query)
    return cursor.fetchone()


def obtenerDatosPais(fecha):
    query = """
        select casos_salon, casos_uci, indice_positividad from datos_pais where fecha = '{fecha}';
    """
    conn = getMyConnection()
    cursor = conn.cursor()
    
    cursor.execute( query.format(fecha = fecha) )
    records = cursor.fetchall()

    datos = {}

    datos['casos_salon'] = records[0][0]
    datos['casos_uci'] = records[0][1]
    datos['indice_positividad'] = str(records[0][2]) + "%"

    return datos

def getPredicciones(mes, semana):
    query = """
        SELECT codigo_distrito, activos, grupo as socio from prediccion_distrito WHERE mes = {mes} and semana = '{semana}'
    """

    conn = getMyConnection()
    cursor = conn.cursor()
    
    cursor.execute( query.format(mes = mes, semana = semana) )
    records = cursor.fetchall()

    datos = {}

    for row in records:
        tupla = {}
        tupla['activos'] = row[1]
        tupla['socio'] = row[2]
        datos[str(row[0])] = tupla

    return datos

def obtenerProyecciones(fecha, muestra):
    query = """
        SELECT codigo_dta, porcentaje, muestra from proyeccion_distrito WHERE fecha_inicio <= '{fecha}' and fecha_fin > '{fecha}' and muestra = {muestra}
    """

    conn = getMyConnection()
    cursor = conn.cursor()
    
    cursor.execute( query.format(fecha = fecha, muestra = muestra) )
    records = cursor.fetchall()

    datos = {}

    for row in records:
        tupla = {}
        tupla['porcentaje'] = row[1]
        tupla['muestra'] = row[2]
        datos[str(row[0])] = tupla

    return datos

def	getQueryPreva( conglomerado ):
	query = """
	select codigo_distr, nom_prov, nom_cant, pendiente, nom_dist, fecha, cantidad, clas_ids
    FROM distrito d, acumulado_distrito ad 
    where d.codigo_distr = ad.codigo_distrito and clas_ids  like '%{conglo}%' order by nom_dist, cantidad;
    """
	return query.format(conglo=conglomerado) 
	
def	getQueryPrevaParams( conglomerado ):
	query = """
	select max(pendiente), min(pendiente), max(cantidad), min(cantidad)
    from acumulado_distrito ad where clas_ids like  '%Muy bajo Desarrollo%';
    """
	return query.format(conglo=conglomerado) 

def getQueryVacunas(fecha):
    query = """
        SELECT vacunas_primera_dosis, vacunas_segunda_dosis, vacunas_primera_dosis + vacunas_segunda_dosis as total_vacunas, to_char(fecha, 'DD-MM-YYYY') FROM datos_pais WHERE fecha = '{fecha}' and vacunas_primera_dosis is not null
    """
    return query.format(fecha = fecha)

def getQueryVacunasDefault():
    query = """
        SELECT vacunas_primera_dosis, vacunas_segunda_dosis, vacunas_primera_dosis + vacunas_segunda_dosis AS total_vacunas, to_char(fecha, 'DD-MM-YYYY') FROM datos_pais WHERE vacunas_primera_dosis IS NOT NULL ORDER BY fecha DESC LIMIT 1
    """
    return query