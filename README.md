## acumulado_distrito
Se almacenarán los datos referentes a la acumulación de todos la información en general con respecto a cada distrito de nuestro país. En esta tabla se tiene control de datos como los casos diarios, cantidad total de casos acumulados, fallecidos, activos, casos del día, órdenes sanitarias y muchos otros más con cada día en específico.

Nombre|Tipo de Dato|Permite nulos|Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
fecha | date | No | Día en el cual se reportan los datos|
codigo_distrito|int|No|Código del distrito|
cantidad|int|Sí|Casos acumulados|
recuperados|int|Sí|Casos recuperados|
fallecidos|int|Sí|Casos de personas fallecidas|
activos|int|Sí|Casos activos|
caso_dia|int|Sí|Casos nuevos|
cant_ord_pers|int|Sí|Cantidad de órdenes sanitarias a personas|
cant_den_pers|int|Sí|Cantidad de denuncias a personas|
cant_ord_est|int|Sí|Cantidad de órdenes sanitarias a locales o establecimientos|
cant_den_est|int|Sí|Cantidad de denuncias a locales o establecimientos|
coef_var|float|Sí|Indica el porcentaje de variación de los casos activos en un distrito por semana, e indica si el distrito presenta variaciones importantes en el tiempo|
ta|int|Sí|Tasa de ataque|
pendiente|int|Sí|Indica el comportamiento de la pendiente de casos activos por covid 19 en el distrito, expresado en un porcentaje|
condicion|varchar|Sí|Nivel de alerta del distrito como amarillo o  naranja|
grupo|varchar|Sí|Índice socio sanitario: muy bajo, bajo, medio, alto, muy alto|
poblacion|int|Sí|Población de un distrito|
---

---

## canton
Esta tabla contiene información sobre territorios indígenas, su cantidad de habitantes, el nombre del pueblo, su representación legal y área.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
ogc_fid |int |Sí |Identificador de objeto geoespacial
wkb_geometry|geometry|No|Serie de puntos geométricos que conforman la figura del cantón en el mapa.
objectid|int|No|Identificador de objeto geoespacial
cod_prov|varchar|No|Código de la  provincia
cod_cant|varchar|No|Código del cantón
nom_prov|varchar|No|El nombre de la provincia
nom_cant_1|varchar|No|El nombre del cantón 
---

---

## datos_distrito
Esta tabla contiene datos socioeconómicos de los habitantes del distrito actual.
Nombre|Tipo de Dato| Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
codigo_distrito|numeric|Sí|Código del distrito actual|
poblacion|int|No|Número de habitantes|
pob_am|float|No|Población adulta mayor|
pob_pobre|float|No|Población en pobreza|
---

---

## datos_pais
Se almacenarán los datos referentes a cada día en específico con respecto a la cantidad de personas hospitalizadas en nuestro país. En la tabla se diferencian los hospitalizados en “salón” a los que se encuentran en Unidad de Cuidados Intensivos y además agrega el índice de positividad.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|fecha|date | No|Día en el cual se reportan los datos.
casos_salon|int|Sí|Cantidad de personas hospitalizadas en salón.
casos_uci|int|Sí|Cantidad de personas hospitalizadas en una Unidad de Cuidados Intensivos.
indice_positividad|float|Sí|Porcentaje de personas que dan positivo en la prueba de COVID-19 entre todas las personas que se hicieron la prueba
vacunas_primera_dosis|int|Sí|Cantidad de primeras dosis de vacunas contra el COVID-19 aplicada en la población.
vacunas_segunda_dosis|int|Sí|Cantidad de seguundas dosis de vacunas contra el COVID-19 aplicada en la población.
---

---

## denuncia_911
Esta tabla contiene datos sobre las denuncias de Covid 19 en cada distrito
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
consecutivo|int|Sí|Denuncias consecutivas en un distrito|
cod_dist|numeric|No|Código del distrito actual|
direccion|varchar|No|Dirección de donde se realizó la denuncia|
fecha|date|No|Fecha en que se hizo la denuncia|
cantidad|int|No|Cantidad de denuncias en el distrito|
---

---

## distrito
Se almacenarán los datos referentes a cada distrito de nuestro país en específico. Dentro de esta tabla se ubican diferentes datos como lo son los de ubicación del distrito, códigos y nombres de provincia - cantón - distrito al que le pertenecen y un ID.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
|ogc_fid |int |No |Identificador de objeto geoespacial
wkb_geometry|geometry|Sí|Serie de puntos geométricos que conforman la figura del cantón en el mapa.
objectid|int|Sí|Identificador de objeto geoespacial
cod_prov|varchar|Sí|Código de la provincia
cod_cant|varchar|Sí|Código del cantón
cod_dist|varchar|Sí|Código del distrito (solo distrito, sin prefijo de cantón y provincia).
codigo|varchar|Sí|Código de distrito completo en formato de hilera
nom_prov|varchar|Sí|Nombre de la provincia 
nom_cant|varchar|Sí|Nombre del cantón
nom_dist|varchar|Sí|Nombre del distrito
id|int|Sí|Id del distrito.
codigo_distr|int|Sí|Código del distrito completo en formato numérico.
---

---

## escenario
Esta tabla ilustra las predicciones o proyecciones de casos activos de covid 19 en una fecha específica.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
fecha|date|Sí|Fecha en el que se lleva a cabo los escenarios|
optimista|float|No|Predicción del menor número de contagios para la fecha|
pesimista|float|No|Predicción del mayor número de contagios para la fecha|
---

---

## hogar
Se almacenarán los datos referentes a un lugar en específico. Dentro de esta tabla se ubican diferentes datos como lo son la provincia, cantón, distrito y la dirección exacta donde se ubica el lugar. Además de esto, se almacenará la latitud y longitud para conocer la ubicación exacta. 
Nombre| Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
provincia|varchar |Sí |Nombre de la provincia
canton|varchar|Sí|Nombre del cantón
distrito|varchar|Sí|Nombre del distrito
direccion|varchar|Sí|Dirección exacta de la vivienda. 
nombre|varchar|Sí|Nombre del lugar
lat|int|Sí|Latitud del lugar
long|int|Sí|Longitud del lugar
wkb_geometry|geometry|Sí|Coordenadas del lugar.
---

---

## morbilidad_distrito
Esta tabla contiene la tasa de morbilidad del distrito actual
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
codigo_distrito|numeric|No|Código del distrito|
morbilidad|float|No|Cantidad de personas que se enferman en el distrito en relación a la población total|
---

---

## ordenes_fecha
Se almacenarán los datos referentes a las órdenes realizadas en una fecha en específico, además se enlazará los datos a un distrito.
Nombre        | Tipo de Dato | Permite nulos | Descripción
:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:
fecha |date |No |Día en el cual se reportan los datos.
cod_distrito|varchar|No|Distrito al que pertenece la orden
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
