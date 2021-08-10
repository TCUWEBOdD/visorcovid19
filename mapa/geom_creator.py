import pandas as pd
import numpy  as np
from mapa.libreria.bd import getMyConnection, closeConnection
from mapa.databaseQueries import *
import folium
import geopandas as gpd
from shapely.geometry import Polygon
import json, os
import jsonpickle

conn = getMyConnection()


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


def get_distNOUSAR(  ):

	fecha = "2020-07-11"
	query =   getQueryDistriAcum( fecha )
	
	query2 = """
		select d.wkb_geometry, d.nom_dist as nombre, d.nom_prov as proInfo, nom_cant as cantInfo
		from distrito2 ;
		"""
		
	df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='wkb_geometry' )
	df['fillColor'] = 'red'
	gjson = df.to_crs(epsg='4326').to_json()

	return gjson #


def get_geom_prov3():
	folium.GeoJson( gjson,   tooltip=folium.GeoJsonTooltip(fields=['nom_cant_1'] , aliases=['Cantón:']),
	style_function=lambda df: {
		'fillColor': df['properties']['color'],
		'color' : df['properties']['linea'],
		'tooltip' : df['properties']['nom_cant_1'],
		'weight' : 0.2,
		'fillOpacity' : 0.4,
		'population': '1000',
	}	).add_to( m )
	
	m = folium.Map(location=[9.934739, -84.087502], zoom_start=7)
	module_dir = os.path.dirname(__file__)   #get current directory
	#file_path = os.path.join(module_dir,'static/mapa/datos/poblados.geojson')  
	file_path = os.path.join(module_dir,'static/mapa/datos/provincias.geojson')  

	#geo_pob = json.load( open( file_path ) ) 
	
	#POINT (490635.7112 1098935.1757)
	
	m = folium.Map(location=[45.5236, -122.6750])
	
	#print( geo_pob )
	folium.GeoJson(geo_pob).add_to(  m );

	#points = folium.features.GeoJson(gjson)

	#m.add_children(points)
	#print( df )
	
	m=m._repr_html_() #updated
	return "pepe" 
	
	
	


def get_geom_prov2():
	#query = "select * from poblado where pueblo like 'URUCA'"
	#df = gpd.GeoDataFrame.from_postgis( query , conn, geom_col='geog', crs="EPSG:4326" )
	#df['geoid'] = df.index.astype(str)
	#jsontxt = df.to_json()
	
	
	#print( jsontxt ) 
	
	#creation of map comes here + business logic
	m = folium.Map(location=[9.934739, -84.087502], zoom_start=7)
	
	#geo_pob = json.load( open( 'static/mapa/datos/poblados.geojson' ))
	
	module_dir = os.path.dirname(__file__)   #get current directory
	file_path = os.path.join(module_dir,'static/mapa/datos/poblados.geojson')  
	geo_pob = json.load(file_path ) 
	
	print( geo_pob )
	#folium.GeoJson(geo_pob).add_to(  m );

	

	#df.loc[0, 'geog' ]

	#test = folium.Html('<b>Mapa Sala Situación</b>', script=True)
	
	
	#mydoc = minidom.parse('static/mapa/Provincias.shp')
	
	#popup = folium.Popup(test, max_width=2650)
	
	#print( df )
	#folium.RegularPolygonMarker(location=[51.5, -0.25], popup=popup).add_to(m)
	

	m=m._repr_html_() #updated
	return m 
	
	


	

