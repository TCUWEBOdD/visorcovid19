# Status de SonarQube
[![Quality Gate Status](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=alert_status)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Code Smells](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=code_smells)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Lines of Code](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=ncloc)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Vulnerabilities](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=vulnerabilities)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Duplicated Lines (%)](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=duplicated_lines_density)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Technical Debt](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=sqale_index)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Maintainability Rating](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=sqale_rating)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Reliability Rating](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=reliability_rating)](http://34.125.17.187:9000/dashboard?id=visorcovid19) [![Security Rating](http://34.125.17.187:9000/api/project_badges/measure?project=visorcovid19&metric=security_rating)](http://34.125.17.187:9000/dashboard?id=visorcovid19)

# Documentación del sistema

La documentación del código fuente está disponible [aquí](https://sebas3552.github.io/covid19docs.github.io/).

# Python docstings

Para autogenerar la documentación del sistema, instale la herramienta PDOC con pip:

```pip install pdoc3```

Luego, en la carpeta raíz del proyecto ejecute el siguiente comando para generar o actualizar la documentación:

```pdoc -o docs --html --skip-errors --force .```


# Documentación de base de datos

## acumulado_distrito
Tabla principal donde se almacenan los datos epidemiológicos por día, desde el inicio de la pandemia en Costa Rica.
Clasifica los datos por fecha y cantón: cantidad de casos acumulados, activos, recuperados, fallecidos y nuevos de COVID-19 reportados por día, así como el cálculo del coeficiente de variación, tasa de ataque, pendiente, y datos como el nivel de alerta del distrito y el índice socio sanitario.
Nombre|Tipo de Dato|Permite nulos|Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
fecha | date | No | Fecha de los datos|
codigo_distrito|int|No|Código del distrito|
cantidad|int|Sí|Casos acumulados|
recuperados|int|Sí|Casos recuperados|
fallecidos|int|Sí|Casos de personas fallecidas|
activos|int|Sí|Casos activos|
caso_dia|int|Sí|Casos nuevos|
coef_var|float|Sí|Coeficiente de variación|
ta|int|Sí|Tasa de ataque|
pendiente|int|Sí|Pendiente|
condicion|varchar|Sí|Nivel de alerta del distrito: amarillo, naranja|
grupo|varchar|Sí|Índice socio sanitario: muy bajo, bajo, medio, alto, muy alto|
---

---

## canton
Contiene datos sobre los cantones de Costa Rica: geometría, código y nombre de provincia a la que pertenece, y código y nombre de cantón.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
ogc_fid |int |Sí |Identificador de objeto geoespacial
wkb_geometry|geometry|No|Serie de puntos geométricos que conforman la figura del cantón en el mapa.
objectid|int|No|Identificador de objeto geoespacial
cod_prov|varchar|No|Código de la provincia a la que pertenece
cod_cant|varchar|No|Código del cantón
nom_prov|varchar|No|Nombre de la provincia a la que pertenece
nom_cant_1|varchar|No|Nombre del cantón 
---

---

## datos_distrito
Contiene datos socioeconómicos de los distritos de Costa Rica: cantidad de habitantes, población adulta mayor y población en pobreza.
Nombre|Tipo de Dato| Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
codigo_distrito|numeric|No|Código del distrito|
poblacion|int|Sí|Cantidad de habitantes|
pob_am|float|Sí|Población adulta mayor|
pob_pobre|float|Sí|Población en pobreza|
---

---

## datos_pais
Contiene datos epidemiológicos a nivel país: cantidad de hospitalizaciones en salón, cantidad de hospitalizaciones en UCI, cálculo del índice de positividad, y cantidad de vacunas por primeras y segundas dosis.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|fecha|date|No|Fecha de los datos.
casos_salon|int|Sí|Cantidad de personas hospitalizadas en salón.
casos_uci|int|Sí|Cantidad de personas hospitalizadas en una Unidad de Cuidados Intensivos.
indice_positividad|float|Sí|Porcentaje de personas que dan positivo en la prueba de COVID-19 entre todas las personas que se hicieron la prueba
vacunas_primera_dosis|int|Sí|Cantidad de primeras dosis de vacunas contra el COVID-19 aplicadas en la población.
vacunas_segunda_dosis|int|Sí|Cantidad de seguundas dosis de vacunas contra el COVID-19 aplicadas en la población.
---

---

## denuncia_911
Contiene datos sobre las denuncias reportadas al 911 por temas relacionados al COVID-19 en cada distrito.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
consecutivo|int|No|Identificador de denuncias.|
cod_dist|numeric|Sí|Código de distrito|
direccion|varchar|Sí|Dirección de donde se realizó la denuncia|
fecha|date|Sí|Fecha en que se reportó la denuncia|
---

---

## distrito
Contiene datos de los distritos de Costa Rica: geometría, código de provincia, código de cantón, código de distrito, nombre de provincia, nombre de cantón y nombre de distrito.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|ogc_fid |int |No |Identificador de objeto geoespacial
wkb_geometry|geometry|Sí|Serie de puntos geométricos que conforman la figura del distrito en el mapa.
objectid|int|Sí|Identificador de objeto geoespacial
cod_prov|varchar|Sí|Código de provincia
cod_cant|varchar|Sí|Código de cantón
cod_dist|varchar|Sí|Código de distrito (solo distrito, sin prefijo de cantón y provincia).
codigo|varchar|Sí|Código de distrito completo en formato de hilera
nom_prov|varchar|Sí|Nombre de provincia 
nom_cant|varchar|Sí|Nombre de cantón
nom_dist|varchar|Sí|Nombre de distrito
id|int|Sí|Id del distrito.
codigo_distr|int|Sí|Código de distrito completo en formato numérico.
---

---

## hogar
Contiene datos de los hogares de ancianos en Costa Rica: nombre y geometría (coordenadas de ubicación).
Nombre| Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
nombre|varchar|Sí|Nombre del lugar
wkb_geometry|geometry|Sí|Coordenadas del lugar.
---

---

## morbilidad_distrito
Contiene el cálculo de la tasa de morbilidad por cada distrito.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
codigo_distrito|numeric|No|Código del distrito|
morbilidad|float|No|Cantidad de personas que se enferman en el distrito en relación a la población total del mismo|
---

---

## ordenes_fecha
Contiene la cantidad de órdenes sanitarias a personas reportadas por distrito y por fecha.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
fecha |date |No|Fecha de las órdenes.
cod_distrito|varchar|No|Distrito de las órdenes.
denuncias_personas|int|Sí|Cantidad de personas denunciadas
---

---

## poblado
Esta tabla contiene la cantidad de habitantes de un pueblo, cantón y provincia específico; así como sus coordenadas.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
ogc_fid|int|Sí|Identificador de objeto geoespacial|
wkb_geometry|geometry|No|Serie de puntos geométricos que conforman la figura del poblado en el mapa|
objectid|int|No|Identificador de objeto geoespacial|
poblac_|int|No|Identificador de poblado|
provincia|varchar|No|Provincia actual|
canton|varchar|No|Cantón actual|
pueblo|varchar|No|Pueblo actual|
poblac_id|int|No|Identificador de poblado|
x|float|No|Coordenada x|
y|float|No|Coordenada y|
---

---

## prediccion_distrito
Se almacenarán los datos referentes a las predicciones que se realizarán para cada distrito de nuestro país según los cálculos realizados a partir de los datos suministrados anteriormente en esta base de datos.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|codigo_distrito |int |No |Código del distrito
nombre_distrito|varchar|Sí|Nombre del distrito
mes|int|No|Número del mes al que pertenecen los datos
semana|varchar|No|Semana a la que pertenecen los datos
activos|int|Sí|Casos activos en el momento específico
prevalencia|int|Sí|Tasa de prevalencia de los casos
acumulado|int|Sí|Casos acumulados en el momento específico
inv_acum|int|Sí| vacío
grupo|varchar|Sí|Índice socio sanitario: muy bajo, bajo, medio, alto, muy alto.
escenario|varchar|Sí|Comportamiento que siguen los casos de COVID-19: positivo, negativo, tendencial.
ano|int|Sí|Año correspondiente a la predicción.
---

---

## provincia
Esta tabla contiene información de la provincia actual y sus dimensiones en el mapa de Costa Rica.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
ogc_fid|int|Sí|Identificador de objeto geoespacial|
wkb_geometry|geometry|No|Serie de puntos geométricos que conforman la figura de la provincia en el mapa|
fid|int|No|Identificador de objeto geoespacial|
nprovincia|varchar|No|Nombre de la provincia|
num_canto|float|No|Número de cantones que posee|
cod_prov|float|No|Código de la provincia|
shape_length|float|No|Largo de la figura|
shape_area|float|No|Área de la figura|
---

---

## terr_indigena
Esta tabla contiene información sobre territorios indígenas, su cantidad de habitantes, el nombre del pueblo, su representación legal y área.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|area_ofi|numeric |No |Área del territorio indígena
pueblo|varchar|No|El pueblo actual
poblacion|numeric|No|Cantidad de habitantes
repre_legal|varchar|No|Nombre oficial del territorio indígena
wbk_geometry|geometry|No|Permite la localización de un lugar en el mapa
---

---
## proyeccion_distrito
Esta tabla contiene información sobre la proyección a realizar en los diferentes distritos existentes.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|codigo_dta|numeric |No |Código del distrito
porcentaje|numeric|Sí|Porcentaje de proyección
fecha_inicio|date|No|Fecha de inicio de proyección
fecha_fin|date|Sí|Fecha de finalización de proyección
muestra|numeric|No|Muestra de población
---


