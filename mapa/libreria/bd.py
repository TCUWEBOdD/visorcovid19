from cryptography.fernet import Fernet
import psycopg2 as psql
import covid_project.settings as sysconf

cwd = sysconf.BASE_DIR + "/covid_project"


def obtenerCredenciales(filename=cwd + "/credenciales.txt"):
    """
    Utilidad para obtener y desencriptar las credenciales almacenadas en el archivo credenciales.txt
    Este archivo tiene todos los parámetros necesarios para realizar la conexión a la BD.

    Parámetros
    ---------
    filename : str
        Ubicación del archivo de credenciales.

    Retorna
    -------
    list
        Lista que contiene las credenciales desencriptadas en formato str codificado como UTF-8.
    """

    usuario = ""
    contrasena = ""
    host = ""
    puerto = ""
    db = ""
    with open(filename, "rb") as archivo_credenciales:
        user = archivo_credenciales.readline()
        passwd = archivo_credenciales.readline()
        hostname = archivo_credenciales.readline()
        port = archivo_credenciales.readline()
        catalog = archivo_credenciales.readline()
        llave = archivo_credenciales.readline()
        f = Fernet(llave)
        usuario = f.decrypt(user)
        contrasena = f.decrypt(passwd)
        host = f.decrypt(hostname)
        puerto = f.decrypt(port)
        db = f.decrypt(catalog)
    return [
        usuario.decode("utf-8"),
        contrasena.decode("utf-8"),
        host.decode("utf-8"),
        puerto.decode("utf-8"),
        db.decode("utf-8"),
    ]


def getConnection(user, password, host, port, db):
    """
    Obtiene la conexión a la base de datos.

    Parámetros
    ----------
    user : str
        Usuario
    password : str
        Contraseña
    host : str
        Servidor de base de datos
    port : str
        Puerto del servidor de base de datos
    database : str
        Catálogo de base de datos

    Retorna
    -------
    connection
        Objeto de conexión a la base de datos.
    """

    connection = None
    connection = psql.connect(
        user=user, password=password, host=host, port=port, database=db
    )

    return connection


def getAuthConnection():
    """
    Inyecta los parámetros necesarios para obtener la conexión a la base de datos.

    Retorna
    -------
    connection
        Objeto de conexión a la base de datos.
    """

    params = obtenerCredenciales()
    return getConnection(params[0], params[1], params[2], params[3], params[4])
    # return getConnection('postgres', 'password', 'localhost', '5432', 'postgres')


def closeConnection(connection):
    """
    Cierra la conexión establecida a la base de datos.

    Parámetros
    ----------
    connection : connection
        Objeto de conexión a la base de datos.
    """

    if connection:
        connection.close()


# forma de cargar un custom
# pg_restore -U covid -d covidinfo2 covid_project-18-10-2020-S.sql
# ogr2ogr -f "PostgreSQL" PG:"host=172.16.9.69 dbname='covidinfo2' user='covid' password='C0vv111d!!'" "C:\Users\diego\Dropbox\Public\paradas.geojson"
