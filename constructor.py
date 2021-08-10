from xml.dom import minidom
from colour import Color
import psycopg2 as psql
import fileinput
from mapa.databaseQueries import getQueryAcumuladosFecha, getQueryProvinceMap, getCasosProvinciaFecha, getMaxCasosProvinciaFecha
from mapa.libreria.bd import getMyConnection, closeConnection

POSTGRES    = 'postgres'
#inicio = Color("#4ee44e")
#colors = list(inicio.range_to(Color("#ff0000"), ))
                                    


#QUERY1 ="select  * from distrito, datos where substring( id::varchar, 1,3 )::int = idparcial order by acumulados asc ;"

#              10%        30       80    
colores = ["#e0d1ac", "#FEF001","#FD9A01","#F00505"]
ratio = [10,30,80, 476]

cursor = None
conn = None
fecha = '2020-10-13'

def getCursor() :
    conn = getMyConnection()
    cursor = conn.cursor()
    return cursor

def closeCursor() :
    if cursor != None :
        cursor.close()
    if conn != None :
        closeConnection(conn)

def crearMapa() :
    global fecha
    query = getQueryAcumuladosFecha( fecha )
    print( query)
    return getXMLMap(query)

def crearProvincia(province) :
    global fecha
    query = getQueryProvinceMap(province, fecha)
    print( query )
    return getXMLMap(query)

def getXMLMap(query):
    mydoc = minidom.parse('mapa/templates/mapa/plantilla_distritos.svg')
    cursor = getCursor()
    cursor.execute(query)
    records = cursor.fetchall()
    g =  mydoc.getElementsByTagName('g')[1]
    populateDocument(mydoc, g, records)
    closeCursor()
    return dumpXml(mydoc)
          
def populateDocument(document, div, queryResult):
    print( len( queryResult ) )
    for row in queryResult:
        hijo = document.createElement("path")
        #hijo.setAttribute("pathid"  , row[1])
        #hijo.setAttribute("class"  , row[9])
        hijo.setAttribute("nom_dist"  ,  row[1] )
        if row[1] == 'SAN MIGUEL' : 
            print( row[1] , row[4] )
        #hijo.setAttribute("d"  , row[4])
        #hijo.setAttribute("style"  , row[7])
        hijo.setAttribute("canton"  , row[2])
        hijo.setAttribute("provincia"  , row[3])
        hijo.setAttribute("cantidad"  , str(row[4]) )
        hijo.setAttribute("recuperados"  , str(row[5]) )
        hijo.setAttribute("fallecidos"  , str(row[6]) )
        hijo.setAttribute("activos"  , str(row[7]) )
        hijo.setAttribute("ta"  , str(row[8]) )
        hijo.setAttribute("coef_var"  , str(row[8]) )
        hijo.setAttribute("pendiente"  , str(row[10]) )
        hijo.setAttribute("condicion"  , str(row[11]) )

        #hijo.setAttribute('inkscape:connector-curvature', '0' )
        #if row[5] != None :
        #    color = calculateColor(row[13]) 
        #    hijo.setAttribute("fill"  , str(row[17]) )
        #else: 
        #    hijo.setAttribute("fill"  , "#A8A8A8" )
        #    hijo.setAttribute("fill-opacity"  , "0.5")
        div.appendChild( hijo )

def dumpXml(document):
    return document.toprettyxml()

def getProvinceMap(query) :
    cursor = getCursor()
    cursor.execute(query)
    records = cursor.fetchall()
    closeCursor()
    jsonResponse = {}
    jsonResponse['distritos'] = []
    for row in records:
        jsonElement = {}
        jsonElement['name_kml'] = row[5]
        jsonElement['canton'] = row[8]
        jsonElement['fill'] = calculateColor(row[10])
        jsonResponse['distritos'].append(jsonElement)
    return jsonResponse


def calculateColor(casesCount) :
    col = colores[0]
    if casesCount is not None: 
        for i in range(len(ratio)):
            if casesCount < ratio[i]:
                col = colores[i]
                break
    return col

def getParametrizedProvinceGaugePlot(column, date, province):
    cursor = getCursor()    
    queryCasos = getCasosProvinciaFecha(column, date, province)
    queryMaxCasos = getMaxCasosProvinciaFecha(date)
    maxCasos = getMaxCasosProvinciaFecha(date)

    cursor.execute(queryCasos)
    records = cursor.fetchall()
    casos = records[0]

    maxCasos = cursor.execute(queryMaxCasos)
    records = cursor.fetchall()
    maxCasos = records[0]
    return gauge(int(casos[0]), int(maxCasos[0]))
