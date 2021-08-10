from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.conf.urls import include, url

urlpatterns= [
	path( 'listarCantones', views.listarCantones, name="listarCantones"),
	path( 'listarDistritos', views.listarDistritos, name="listarDistritos"),
	path( 'getLineChart', views.getLineChart, name="getLineChart"),
	path( 'getGaugeChart', views.getGaugeChart, name="getGaugeChart"),
	path( 'getMap', views.getMap, name="getMap"),
	path( 'getPlots', views.getPlots, name="getPlots"),
	path( 'get_leaflet_cant', views.get_leaflet_cant, name="get_leaflet_cant"),
	path( 'get_leaflet_prov', views.get_leaflet_prov, name="get_leaflet_prov"),
	path( 'getVacunas', views.getVacunas, name="getVacunas"),
	path( 'get_leaflet_dist', views.get_leaflet_dist, name="get_leaflet_dist"),
	path( 'get_json_sedes', views.get_json_sedes, name="get_json_sedes"),
	path( 'get_json_hogares', views.get_json_hogares, name="get_json_hogares"),
	path( 'get_json_indigenas', views.get_json_indigenas, name="get_json_indigenas"),
	path( 'getPrediccionesMapa', views.getPrediccionesMapa, name="getPrediccionesMapa"),
	path( 'getUltimaFecha', views.getUltimaFecha, name="getUltimaFecha"),
	path( 'getDatosPais', views.getDatosPais, name="getDatosPais"),
	path( 'getValidDates', views.getValidDates, name="getValidDates"),
	path( 'getProyecciones', views.getProyecciones, name="getProyecciones"),
	path( 'analytics', views.analytics, name="analytics"),
	url(r'^$', views.home, name="home")
]
