from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from mapa.graficador import *
from mapa.databaseQueries import getCantones, get_dist, getLastDate


def home(request):
    return render(request, "mapa/geo3.html")


def listarCantones(request):
    datos = {"cantones": getCantones(request.GET.get("id"))}
    return JsonResponse(datos)


def listarDistritos(request):
    datos = {"distritos": getDistritos(request.GET.get("id"))}
    return JsonResponse(datos)


def getGaugeChart(request):
    provincia = request.GET.get("province")
    canton = request.GET.get("canton")
    distrito = request.GET.get("distrito")
    fecha = request.GET.get("fecha")
    response = {}
    response["chart"] = gauge_cuad(fecha, provincia, canton, distrito)
    return JsonResponse(response)


def getVacunas(request):
    fecha = request.GET.get("fecha")
    response = {}
    response["chart"] = gauge_vacunas(fecha)
    return JsonResponse(response)


def getPlots(number):
    response = {}
    response["plot2"] = nacional()
    response["graficoVacunas"] = grafico_progreso()
    return JsonResponse(response)


def get_leaflet_dist(request):
    date = request.GET.get("date")
    response = {}
    response["capas"] = get_dist(date)
    return JsonResponse(response)


def get_json_sedes(request):
    response = {}
    response["capas"] = get_sedes()
    return JsonResponse(response)


def get_json_hogares(request):
    response = {}
    response["capas"] = get_hogares()
    return JsonResponse(response)


def get_json_indigenas(request):
    response = {}
    response["capas"] = get_indigenas()
    return JsonResponse(response)


def analytics(request):
    return render(request, "mapa/analytics.html")


def getPrediccionesMapa(request):
    response = {}
    mes = request.GET.get("mes")
    semana = request.GET.get("semana")
    response["predicciones"] = getPredicciones(mes, semana)
    return JsonResponse(response)


def getUltimaFecha(request):
    response = {}
    response["date"] = getLastDate()
    return JsonResponse(response)


def getDatosPais(request):
    response = {}
    fecha = request.GET.get("fecha")
    response["datos_pais"] = obtenerDatosPais(fecha)
    return JsonResponse(response)


def getValidDates(request):
    response = {}
    response["fechas"] = getFechasValidas()
    return JsonResponse(response)


def getProyecciones(request):
    response = {}
    fecha = request.GET.get("fecha")
    muestra = request.GET.get("muestra")
    response["proyecciones"] = obtenerProyecciones(fecha, muestra)
    return JsonResponse(response)
