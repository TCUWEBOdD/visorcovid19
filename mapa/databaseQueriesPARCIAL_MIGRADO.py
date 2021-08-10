import psycopg2 as psql
from mapa.libreria.bd import getMyConnection
import geopandas as gpd

conn = getMyConnection()


#VIEJO
def getCantones(province):
    conn = getMyConnection()
    cursor = conn.cursor()

    getCantonesQuery = "select distinct nom_cant from distrito where nom_prov = '{provincia}' order by nom_cant;"
    
    cursor.execute( getCantonesQuery.format(provincia = province) )
    records = cursor.fetchall()

    cantones = []
 
    for row in records:
        cantones.append(row[0])

    return cantones

#MIGRADO
def getCantones(province):
    conn = getMyConnection()
    cursor = conn.cursor()
    getCantonesQuery = """
        select c.nombre from canton c join provincia p 
        on c.id_provincia = p.id
        and p.nombre = '{provincia}'
    """

    cursor.execute( getCantonesQuery.format(provincia = province) )
    records = cursor.fetchall()

    cantones = []
 
    for row in records:
        cantones.append(row[0])

    return cantones


#Retorna la cantidad de casos acumulados, recuperados y activos para una provincia dada
#VIEJO
def getQueryProvincia( nombre ):
    query = """
    select  fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum( activos) as activos, sum(caso_dia) as caso_dia
    from ( select distinct id, nom_prov, nom_cant, nom_dist as distrito from distrito ) as d, acumulado_distrito a
    where a.codigo_distrito = d.id
	and d.nom_prov = '{province}'
    group by fecha order by fecha asc;"""
    
    return query.format(province = nombre)

#MIGRADO
def getQueryProvincia(nombre):
    query = """
        select f.fecha, ac.cantidad as acumulados, re.cantidad as recuperados, act.cantidad as activos
        from (select distinct id, nombre, id_canton from distrito) as d, casos as ac, casos as re, casos as act, fecha as f, canton as c, provincia as p
        where ac.tipo = 'acumulados' and ac.id_distrito = d.id and ac.fecha = f.fecha
        and re.tipo = 'recuperados' and re.id_distrito = d.id and re.fecha = f.fecha
        and act.tipo = 'activos' and act.id_distrito = d.id and act.fecha = f.fecha
        and d.id_canton = c.id
        and p.nombre = '{nombre}'
        and c.id_provincia = p.id
        group by f.fecha, ac.cantidad, re.cantidad, act.cantidad
    """

    return query.format(province = nombre)


#VIEJO
def getQueryCantonVIEJO(provincia, canton):
    query = """
    select  fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum( activos) as activos, sum(caso_dia) as caso_dia
    from ( select distinct id, nom_prov, nom_cant, nom_dist as distrito from distrito ) as d, acumulado_distrito a
    where a.codigo_distrito = d.id
	and d.nom_prov = '{province}'
    and d.nom_cant = '{canton}'
    group by fecha order by fecha asc;"""
    return query.format(province = provincia, canton = canton)


#MIGRADO
def getQueryCantonMIGRADO(provincia, canton):
    query = """
	 select  fecha, sum(cantidad) as acumulados, sum(recuperados) as recuperados, sum( activos) as activos, sum(caso_dia) as caso_dia
    from ( select distinct id, nom_prov, nom_cant, nom_dist as distrito from distrito ) as d, acumulado_distrito a
    where a.codigo_distrito = d.id
	and d.nom_prov = '{province}'
	and d.nom_prov = '{canton}'
    group by fecha order by fecha asc;
    """
    return query.format(province = provincia, canton = canton)


# Obtiene la cantidad de casos acumulados, activos, recuperados y 
#VIEJO
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

# * MIGRADO
def getQueryDistrito(provincia, canton, distrito):
    query = """
        select f.fecha, ac.cantidad as acumulados, re.cantidad as recuperados, act.cantidad as activos
        from (select distinct id, nombre, id_canton from distrito) as d, casos as ac, casos as re, casos as act, fecha as f, canton as c, provincia as p
        where ac.tipo = 'acumulados' and ac.id_distrito = d.id and ac.fecha = f.fecha
        and re.tipo = 'recuperados' and re.id_distrito = d.id and re.fecha = f.fecha
        and act.tipo = 'activos' and act.id_distrito = d.id and act.fecha = f.fecha
        and d.nombre = '{distrito}'
        and c.nombre = '{canton}'
        and d.id_canton = c.id
        and p.nombre = '{province}'
        and c.id_provincia = p.id
        group by f.fecha, ac.cantidad, re.cantidad, act.cantidad
    """
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

# VIEJO
def getMaxCasosProvinciaFecha(date):
    query = """
    select max(sum) from (
        select sum(ad.cantidad), d.nom_prov from acumulado_distrito ad join distrito d on ad.codigo_distrito = d.id
        where fecha = '{fecha}'
        group by d.nom_prov
	) acumulados
    """
    return query.format(fecha = date)


#MIGRADO
def getMaxCasosProvinciaFecha(date):
    query = """
        select max(sum) from (
        select sum(ad.cantidad), c.id_provincia from casos ad join distrito d on ad.id_distrito = d.id
		join canton c on d.id_canton = c.id
        where fecha = '{fecha}'
		group by c.id_provincia
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

	
def getQueryOrdenesPers(  ):
    query = """
	select 	sum(cant_ord_pers) as pers, sum(cant_den_pers) as den  from  ordenes_pers;
    """
    return query 

def getQueryOrdenesPersProv( provincia ):
	query = """
	select 	sum(cant_ord_pers) as pers, sum(cant_den_pers) as den 
	from  ordenes_pers where substring( codigo::varchar, 1,1 ) = ( select fid::varchar 
	from provincia p where LOWER( p.nprovincia )  = LOWER('{province}') );
	"""
	return query.format(province = provincia)

	
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

def get_dist(fecha):
	query = """
		select d.wkb_geometry, d.nom_dist as nombre, d.nom_prov as proInfo, nom_cant as cantInfo,
		( select cantidad as activos from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select ta  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select pendiente from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select recuperados from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select coef_var  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select clas_ids as socio   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select ids_salud  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}'),
		( select condicion   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '{fecha}')
		from distrito d;
		"""
		
	df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
	df['fillColor'] = 'red'
	gjson = df.to_crs(epsg='4326').to_json()

	return gjson 
	
	
def getLastDate():
    conn = getAuthConnection()
    cursor = conn.cursor()
    query = "select fecha from acumulado_distrito ad order by fecha desc limit 1"
    cursor.execute(query)
    return cursor.fetchone()[0].strftime('%Y-%m-%d')
	

def	getQueryPreva( conglomerado ):
	query = """
	select codigo_distr, nom_prov, nom_cant, pendiente, nom_dist, fecha, cantidad, clas_ids
    FROM distrito2 d, acumulado_distrito ad 
    where d.codigo_distr = ad.codigo_distrito and clas_ids  like '%{conglo}%' order by nom_dist, cantidad;
    """
	return query.format(conglo=conglomerado) 
	
def	getQueryPrevaParams( conglomerado ):
	query = """
	select max(pendiente), min(pendiente), max(cantidad), min(cantidad)
    from acumulado_distrito ad where clas_ids like  '%Muy bajo Desarrollo%';
    """
	return query.format(conglo=conglomerado) 


def	getQueryDistriAcum( fecha ):
	query = """
		select d.wkb_geometry, d.nom_dist as nombre, d.nom_prov as proInfo, nom_cant as cantInfo,
		( select cantidad as activos from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select ta  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select pendiente from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select recuperados from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select coef_var  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select grupo as socio   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select ids_salud  from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select condicion   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%'),
		( select clas_ids   from acumulado_distrito a where a.codigo_distrito = d.codigo_distr and fecha = '%{fecha_max}%')
		from distrito d;
		"""
	return query.format(fecha_max=fecha) 




	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	