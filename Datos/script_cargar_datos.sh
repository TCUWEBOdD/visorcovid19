# 1. Descargar archivos de datos de Agustín desde Dropbox 
python3 -c 'import sys; sys.path.append("/home/odd/plataformacovid19/Datos/"); from descarga import descargar_zip; descargar_zip()' 

# 2. Descomprimir los archivos
unzip -d /home/odd/plataformacovid19/Datos/ "/home/odd/plataformacovid19/Datos/FTP COVID-19.zip"

# 3. Ejecutar el cargador de datos
python3 -c 'import sys; sys.path.append("/home/odd/plataformacovid19/Datos/"); from carga_datos import cargarDatos; cargarDatos("/home/odd/plataformacovid19/Datos/COVID19CR.xlsx", "/home/odd/plataformacovid19/Datos/EscenariosOctubre.xlsx")'  

# 4. Ejecutar el crawler para recopilar datos de vacunación de la página de la CCSS
source /home/odd/plataformacovid19/crawler/venv/bin/activate

cd /home/odd/plataformacovid19/crawler/vacunas

scrapy crawl vacunas

# 5. Remover archivos descargados
rm -f /home/odd/plataformacovid19/Datos/*.xlsx
rm -f /home/odd/plataformacovid19/Datos/*.csv
rm -f /home/odd/plataformacovid19/Datos/*.zip
rm -f /home/odd/plataformacovid19/Datos/*.xls