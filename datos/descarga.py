import wget


def descargar_zip():
    """
    Función invocada por el cron job para descargar la carpeta comprimida que contiene los archivos
    necesarios para actualizar los datos del sistema.
    """
    url = "https://www.dropbox.com/sh/jmi6whnby120bwk/AAA0S79smWR61RyRRYO7tPpDa?dl=1"
    wget.download(url, out="/home/odd/plataformacovid19/Datos/FTP COVID-19.zip")
