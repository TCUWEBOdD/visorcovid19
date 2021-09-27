from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from mapa.libreria.bd import getAuthConnection, closeConnection
from mapa.databaseQueries import *
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import random
import covid_project.settings as sysconf

CANT_CASOS = 100
PLOT_SIZE = 170

cwd = sysconf.BASE_DIR


def nacional():
    """
    Genera el gráfico de Indicadores nacionales, que contiene los datos de casos activos, nuevos y recuperados, durante toda la pandemia.

    Retorna
    -------
    str
        Gráfico generado en formato html para ser empotrado en la vista.
    """

    query = getQueryNacional()

    conn = getAuthConnection()

    df = pd.read_sql(query, conn)

    fig = make_subplots(specs=[[{"secondary_y": True}]], rows=1, cols=1)

    fig.add_trace(
        go.Scatter(
            x=df.iloc[:, 0].values,
            y=df.iloc[:, 3].values,
            name="Activos",
            line=dict(color="red"),
        ),
        secondary_y=True,
        row=1,
        col=1,
    )

    # barras de casos nuevos por día
    fig.add_trace(
        go.Bar(
            x=df.iloc[:, 0].values,
            y=df.iloc[:, 4].values,
            name="Nuevos",
            marker_color="gray",
        ),
        secondary_y=False,
        row=1,
        col=1,
    )

    # línea de casos recuperados
    fig.add_trace(
        go.Scatter(
            x=df.iloc[:, 0].values,
            y=df.iloc[:, 2].values,
            mode="lines+markers",
            name="Recuperados",
            line=dict(color="blue"),
        ),
        secondary_y=False,
        row=1,
        col=1,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=5, b=5),
        plot_bgcolor="white",
        height=PLOT_SIZE * 2,
        legend=dict(
            x=0.1,
            y=0.95,
            traceorder="normal",
            font=dict(
                size=12,
            ),
        ),
    )

    fig.update_layout(
        legend=dict(yanchor="top", y=1, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgb(240, 240, 240)")

    plt_div = plot(fig, output_type="div")

    closeConnection(conn)

    return plt_div


def gauge_vacunas(fecha):
    """
    Genera los gráficos de tipo Gauge que contienen los datos de vacunas aplicadas hasta la última fecha registrada en la base de datos.
    Los datos de vacunas aplicadas se obtienen automáticamente de la página de la [CCSS](https://www.ccss.sa.cr/web/coronavirus/vacunacion).

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos en el gráfico.

    Retorna
    -------
    str
        Gráfico de tipo subplots generado en formato html para ser empotrado en la vista.
    """

    query = getQueryVacunas(fecha)

    conn = getAuthConnection()

    df = pd.read_sql(query, conn)

    # Obtiene los datos de vacunación de la fecha del visor, y si no hay datos, carga la última fecha en la que hay datos
    if len(df) == 0:
        query = getQueryVacunasDefault()
        df = pd.read_sql(query, conn)

    total = df.iloc[0, 2]
    fecha = df.iloc[0, 3]

    fig = make_subplots(
        specs=[[{"type": "indicator"}], [{"type": "indicator"}]],
        rows=2,
        cols=1,
        row_heights=[0.5, 0.5],
    )

    grafico = go.Indicator(
        mode="gauge+number+delta",
        value=total,
        domain={"x": [0, 1], "y": [0, 1]},
        # delta = {'reference': 380}, se puede colocar como referencia el total de vacunas de la fecha anterior
        title={"text": "Total de vacunas aplicadas al " + str(fecha)},
        gauge={
            "axis": {"range": [None, 7400000]},
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 7400000,
            },
        },
        number={
            "valueformat": "," + str(2) + "f",
        },
    )

    barras = gauge_estimacion_vacunas()

    fig.add_trace(grafico, row=1, col=1)
    fig.add_trace(barras, row=2, col=1)

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=650)

    plt_div = plot(fig, output_type="div")

    closeConnection(conn)

    return plt_div


def gauge_cuad(fecha, provincia=None, canton=None, distrito=None):
    """
    Genera los gráficos de órdenes sanitarias que contienen los datos de órdenes sanitarias a personas por fecha, y el crecimiento de las órdenes
    sanitarias durante toda la pandemia. Ambos cuentan con resolución a nivel nacional, provincial, cantonal y distrital.

    Parámetros
    ----------
    fecha : str
        Fecha para la cual se desea obtener los datos en el gráfico de órdenes sanitarias por fecha (el de tipo Gauge).
    provincia : str
        Provincia a la cual se quiere limitar el ámbito de los datos en los gráficos.
    canton : str
        Cantón al cual se quiere limitar el ámbito de los datos en los gráficos.
    distrito : str
        Distrito al cual se quiere limitar el ámbito de los datos en los gráficos.

    Retorna
    -------
    str
        Gráfico de tipo subplots generado en formato html para ser empotrado en la vista.
    """

    fig = make_subplots(
        specs=[[{"type": "indicator"}], [{"type": "scatter"}]],
        rows=2,
        cols=1,
        row_heights=[0.3, 0.7],
    )

    # Query para gráfico gauge en una fecha específica
    if provincia == "Todas":
        query = getQueryOrdenesPers(fecha)
    else:
        if distrito != None and distrito != "" and distrito != "NONE":
            query = getQueryOrdenesPersDist(fecha, provincia, canton, distrito)
        elif canton != None and canton != "" and canton != "NONE":
            query = getQueryOrdenesPersCanton(fecha, provincia, canton)
        elif provincia != None and provincia != "" and provincia != "NONE":
            query = getQueryOrdenesPersProv(fecha, provincia)
        else:
            query = getQueryOrdenesPers(fecha)

    conn = getAuthConnection()

    df = pd.read_sql(query, conn)
    if df.empty or df.iloc[0, 0] is None:
        ordenesPersonas = 0
    else:
        ordenesPersonas = df.iloc[0, 0]

    gauge = go.Indicator(
        mode="gauge+number",
        value=ordenesPersonas,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Órdenes sanitarias a personas"},
        number={
            "valueformat": "," + str(2) + "f",
        },
        gauge={
            "axis": {"range": [None, ordenesPersonas * 1.2]},
            "steps": [
                {"range": [0, ordenesPersonas * 0.4], "color": "#ffea00"},
                {
                    "range": [ordenesPersonas * 0.4, ordenesPersonas * 0.6],
                    "color": "orange",
                },
                {
                    "range": [ordenesPersonas * 0.6, ordenesPersonas * 1.1],
                    "color": "red",
                },
            ],
            "threshold": {
                "line": {"color": "#013220", "width": 4},
                "thickness": 0.75,
                "value": ordenesPersonas,
            },
        },
    )

    # Query para gráfico scatter, para todas las fechas
    if provincia == "Todas":
        query = getQueryOrdenesPers(None)
    else:
        if distrito != None and distrito != "" and distrito != "NONE":
            query = getQueryOrdenesPersDist(None, provincia, canton, distrito)
        elif canton != None and canton != "" and canton != "NONE":
            query = getQueryOrdenesPersCanton(None, provincia, canton)
        elif provincia != None and provincia != "" and provincia != "NONE":
            query = getQueryOrdenesPersProv(None, provincia)
        else:
            query = getQueryOrdenesPers(None)

    df = pd.read_sql(query, conn)

    scatter = go.Scatter(
        x=df.iloc[:, 2].values,
        y=df.iloc[:, 0].values,
        name="Órdenes",
        line=dict(color="red"),
        mode="lines",
    )

    fig.add_trace(gauge, row=1, col=1)

    fig.add_trace(scatter, row=2, col=1)

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=700)

    fig.update_xaxes(showgrid=False, title="Tiempo")
    fig.update_yaxes(gridcolor="rgb(240, 240, 240)", title="Órdenes sanitarias")

    plt_div = plot(fig, output_type="div")

    closeConnection(conn)

    return plt_div


def grafico_progreso():
    """
    Genera el gráfico de Dosis estimadas aplicables y efectivas aplicables a partir de los datos de vacunación que se obtengan del archivo
    vacunas_2.csv, mismo que es generado mediante el script estimacion_vacunas.py teniendo como insumos los archivos efectivas.csv y vacunas.csv.
    Estos dos archivos son actualizados manualmente obteniendo los datos de la página de vacunación del [CNE](https://www.cne.go.cr/covid/ADQUISICION_VACUNAS.aspx)
    y del noticiero digital [Delfino.cr](ino.cr/2021/07/ccss-aplico-81-mil-vacunas-la-semana-pasada-y-pais-alcanza-1-7-millones-de-personas-con-al-menos-1-dosis).

    Retorna
    -------
    str
        Gráfico generado en formato html para ser empotrado en la vista.
    """

    df = pd.read_csv(cwd + "/vacunacion/vacunas_v2.csv")
    fig1 = go.Figure()
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])

    fig1.add_trace(
        go.Scatter(
            x=df["fecha"],
            y=df["total"],
            name="Dosis Estimadas",
            line=dict(color="blue"),
        ),
        secondary_y=False,
    )

    fig1.add_trace(
        go.Scatter(
            x=df["fecha"],
            y=df["efect"],
            name="Dosis Aplicadas",
            line=dict(
                color="red",
            ),
        ),
        secondary_y=False,
    )

    fig1.add_trace(
        go.Bar(
            x=df["fecha"],
            y=df["reservas_reales"],
            name="Estimación de Reserva",
            marker_color="rgb(158, 178, 225)",
            opacity=0.6,
            width=[0.2],
        ),
        secondary_y=True,
    )

    fig1.update_layout(
        title="Dosis Estimadas Aplicables y Efectivas Aplicadas",
        xaxis_title="Semana de la Campaña de Vacunación",
    )

    fig1.update_yaxes(title_text="Dosis Aplicadas", secondary_y=False)

    fig1.update_yaxes(title_text="Reserva Estimada", secondary_y=True)

    fig1.update_layout(
        legend=dict(yanchor="top", y=1, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)")
    )

    fig1.update_xaxes(showgrid=False)
    fig1.update_yaxes(gridcolor="rgb(240, 240, 240)")

    plt_div = plot(fig1, output_type="div")
    return plt_div


def estimador_semanas(
    cantidad_vacunas=list,
):
    """
    Genera la estimación de la cantidad de semanas necesarias para alcanzar la inmunidad de rebaño en Costa Rica (al menos el 75% de la
    población con las dos dosis).

    Parámetros
    ----------
    cantidad_vacunas : list
        Lista de la cantidad de vacunas aplicadas en el país por semana.

    Retorna
    -------
    tuple
        Tupla que contiene la cantidad de semanas de vacunación actuales (como referencia), y la cantidad estimada para alcanzar la inmunidad de rebaño.
    """

    meta = 7600000  # meta de vacunación con 2 dosis al 75% de la población de C.R.
    aplicadas = sum(cantidad_vacunas)
    semanas = len(cantidad_vacunas)
    promedio_aplicadas = np.mean(
        cantidad_vacunas[-4:]
    )  # toma el promedio de vacunas aplicadas de las últimas 4 semanas para estimar
    poblacion_restante = meta - aplicadas
    semanas_restantes = int(poblacion_restante / promedio_aplicadas) + 1
    semanas_totales = semanas + semanas_restantes
    return semanas_totales, semanas_restantes


def grafico_gauge(cantidad_vacunas=list):  # r grado de aplicación de 0.5-1
    """
    Genera el gráfico de la estimación de la cantidad de semanas necesarias para alcanzar la inmunidad de rebaño en Costa Rica.

    Parámetros
    ----------
    cantidad_vacunas : list
        Lista de la cantidad de vacunas llegadas al país en cada entrega realizada.

    Retorna
    -------
    Figure
        Gráfico Gauge que contiene los datos de la estimación para alcanzar la inmunidad de rebaño.
    """

    semanas, estimacion_semanas = estimador_semanas(cantidad_vacunas=cantidad_vacunas)
    fig = go.Indicator(
        mode="gauge+number+delta",
        value=semanas - estimacion_semanas,
        domain={"x": [0, 1], "y": [0, 1]},
        delta={
            "reference": semanas
        },  # se puede colocar como referencia el total de vacunas de la fecha anterior
        title={"text": "Semanas para inmunidad al 75%"},
        gauge={
            "axis": {"range": [None, semanas]},
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": semanas,
            },
        },
        number={
            "valueformat": "," + str(2) + "f",
        },
    )

    return fig


def gauge_estimacion_vacunas():
    """
    Genera el gráfico de la estimación de la cantidad de semanas necesarias para alcanzar la inmunidad de rebaño en Costa Rica, a partir
    de los datos de vacunación del archivo vacunas_v2.csv, mismo que es generado mediante el script estimacion_vacunas.py teniendo como
    insumos los archivos efectivas.csv y vacunas.csv. Estos dos archivos son actualizados manualmente obteniendo los datos de la página de
    vacunación del [CNE](https://www.cne.go.cr/covid/ADQUISICION_VACUNAS.aspx) y del noticiero digital
    [Delfino.cr](ino.cr/2021/07/ccss-aplico-81-mil-vacunas-la-semana-pasada-y-pais-alcanza-1-7-millones-de-personas-con-al-menos-1-dosis).

    Retorna
    -------
    str
        Gráfico generado en formato html para ser empotrado en la vista.
    """
    df = pd.read_csv(cwd + "/vacunacion/vacunas_v2.csv")

    aplicadas = df["efect"].tolist()

    return grafico_gauge(cantidad_vacunas=aplicadas)
