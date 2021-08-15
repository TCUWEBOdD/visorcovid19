import wget
import covid_project.settings as sysconf

cwd = sysconf.BASE_DIR


def descargar_zip():
    """
    Función invocada por el cron job para descargar la carpeta comprimida que contiene los archivos
    necesarios para actualizar los datos del sistema.
    """
    url = "https://www.dropbox.com/sh/jmi6whnby120bwk/AAA0S79smWR61RyRRYO7tPpDa?dl=1"
    wget.download(url, out=cwd + "/datos/FTP COVID-19.zip")
