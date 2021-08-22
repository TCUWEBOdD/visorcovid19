from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from mapa.graficador import *
from mapa.databaseQueries import getCantones, get_dist, getLastDate


@require_GET
def home(request):
    """
    Página por defecto al acceder a la plataforma.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene el HTML de la página principal.
    """

    return render(request, "mapa/geo3.html")


@require_GET
def analytics(request):
    """
    Página que contiene los datos de Google Analytics de la plataforma a través de un panel de PowerBI empotrado.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene el HTML de la página de analytics.
    """

    return render(request, "mapa/analytics.html")


@require_GET
def listarCantones(request):
    """
    Obtiene la lista de cantones de una provincia dada.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo el id (nombre) de provincia.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene los cantones de la provincia solicitada en formato JSON.
    """

    datos = {"cantones": getCantones(request.GET.get("id"))}
    return JsonResponse(datos)


@require_GET
def listarDistritos(request):
    """
    Obtiene la lista de distritos de un cantón dado.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo el id (nombre) del cantón.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene los distritos del cantón solicitado en formato JSON.
    """

    datos = {"distritos": getDistritos(request.GET.get("id"))}
    return JsonResponse(datos)


@require_GET
def getGaugeChart(request):
    """
    Obtiene los gráficos de órdenes sanitarias, para una fecha dada (solo el Gauge) y provincia, cantón, distrito, o a nivel nacional.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo la fecha para la cual se solicitan los datos, y opcionalmente los datos de nombre de provincia,
        nombre de cantón y nombre de distrito al cual se desea limitar el gráfico Gauge.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene el gráfico en formato JSON para empotrar en la vista.
    """

    provincia = request.GET.get("province")
    canton = request.GET.get("canton")
    distrito = request.GET.get("distrito")
    fecha = request.GET.get("fecha")
    response = {}
    response["chart"] = gauge_cuad(fecha, provincia, canton, distrito)
    return JsonResponse(response)


@require_GET
def getVacunas(request):
    """
    Obtiene el gráfico tipo Gauge que contiene los datos de la cantidad de vacunas aplicadas en una fecha determinada.
    El gráfico se construye tanto para una fecha específica, o bien para la última fecha conocida, por defecto.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo la fecha para la cual se solicitan los datos.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene el gráfico en formato JSON para empotrar en la vista.
    """

    fecha = request.GET.get("fecha")
    response = {}
    response["chart"] = gauge_vacunas(fecha)
    return JsonResponse(response)


@require_GET
def getPlots(request):
    """
    Obtiene los gráficos de Indicadores Nacionales y Dosis estimadas aplicables y efectivas aplicadas.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene los gráficos en formato JSON para empotrar en la vista.
    """

    response = {}
    response["plot2"] = nacional()
    response["graficoVacunas"] = grafico_progreso()
    return JsonResponse(response)


@require_GET
def get_leaflet_dist(request):
    """
    Obtiene la capa de distritos del mapa, con todos sus metadatos, en una fecha dada.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo la fecha para la cual se solicitan los datos.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la capa de distritos y sus metadatos en formato JSON para empotrar en el mapa.
    """

    date = request.GET.get("date")
    response = {}
    response["capas"] = get_dist(date)
    return JsonResponse(response)


@require_GET
def get_json_sedes(request):
    """
    Obtiene la capa de sedes del examen de admisión de universidades públicas y sus respectivos metadatos.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la capa de sedes del examen de admisión y sus metadatos en formato JSON para empotrar en el mapa.
    """

    response = {}
    response["capas"] = get_sedes()
    return JsonResponse(response)


@require_GET
def get_json_hogares(request):
    """
    Obtiene la capa de hogares de ancianos del país y sus respectivos metadatos.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la capa de hogares de ancianos del país y sus metadatos en formato JSON para empotrar en el mapa.
    """

    response = {}
    response["capas"] = get_hogares()
    return JsonResponse(response)


@require_GET
def get_json_indigenas(request):
    """
    Obtiene la capa de asentamientos indígenas del país y sus respectivos metadatos.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la capa de asentamientos indígenas y sus metadatos en formato JSON para empotrar en el mapa.
    """

    response = {}
    response["capas"] = get_indigenas()
    return JsonResponse(response)


@require_GET
def getPrediccionesMapa(request):
    """
    Obtiene los datos de predicciones de casos activos por distrito, para un mes y semana dados.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene los datos de predicciones de casos activos en formato JSON para empotrar en el mapa.
    """

    response = {}
    mes = request.GET.get("mes")
    semana = request.GET.get("semana")
    response["predicciones"] = getPredicciones(mes, semana)
    return JsonResponse(response)


@require_GET
def getUltimaFecha(request):
    """
    Obtiene la fecha más reciente registrada para la que se conocen datos en la base de datos.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la fecha más reciente disponible en la base de datos en formato JSON.
    """

    response = {}
    response["date"] = getLastDate()
    return JsonResponse(response)


@require_GET
def getDatosPais(request):
    """
    Obtiene los datos a nivel país de hospitalizaciones en salón, en UCI e índice de positividad, en una fecha dada.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo la fecha para la que se solicitan los datos.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene los datos de hospitalizaciones e índice de positividad a nivel país, de la fecha solicitada,
        en formato JSON para empotrar en la vista.
    """

    response = {}
    fecha = request.GET.get("fecha")
    response["datos_pais"] = obtenerDatosPais(fecha)
    return JsonResponse(response)


@require_GET
def getValidDates(request):
    """
    Obtiene todas las fechas registradas en la tabla acumulado_distrito, es decir, son las fechas para las cuales hay datos.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la lista de las fechas válidas en formato JSON.
    """

    response = {}
    response["fechas"] = getFechasValidas()
    return JsonResponse(response)


@require_GET
def getProyecciones(request):
    """
    Obtiene la capa de proyecciones para muestras determinadas de distritos, para una fecha que caiga en el rango de una proyección registrada en la base de datos.

    Parámetros
    ----------
    request : HttpRequest
        HTTP request enviada al servidor, incluyendo la fecha y el tamaño de muestra para los cuales se solicitan los datos.

    Retorna
    -------
    HttpResponse
        HTTP Response que contiene la capa de proyecciones y sus metadatos en formato JSON para empotrar en el mapa.
    """

    response = {}
    fecha = request.GET.get("fecha")
    muestra = request.GET.get("muestra")
    response["proyecciones"] = obtenerProyecciones(fecha, muestra)
    return JsonResponse(response)
