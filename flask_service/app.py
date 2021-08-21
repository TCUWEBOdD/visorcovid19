from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from mapa.libreria.bd import obtenerCredenciales
from mapa.libreria.notificador.notificador import Notificador

app = Flask(__name__)

USUARIO = 0
PASS = 1
HOST = 2
PORT = 3
DB = 4

creds = obtenerCredenciales()

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://"
    + creds[USUARIO]
    + ":"
    + creds[PASS]
    + "@"
    + creds[HOST]
    + ":"
    + creds[PORT]
    + "/"
    + creds[DB]
)

db = SQLAlchemy(app)

TOKEN_DEFINED = "F91D3F51E49063C170D0528A567221498A0BC1E68CE06ADDE4D81C28AD9396DC"
"""Token de autenticación para utilizar el API."""


class denuncia_911(db.Model):
    """
    Clase utilizada para modelar el API de carga de datos de denuncias al 911.
    Posee las rutas / y /denuncia 911.

    Atributos
    ---------
    consecutivo
        Columna del número de consecutivo de la denuncia en la base de datos.
    cod_dist
        Columna del código de distrito asociado a la denuncia en la base de datos.
    direccion
        Columna de la dirección fisica en la que se reportó la denuncia en la base de datos.
    fecha
        Columna de la fecha en la que se reportó la denuncia en la base de datos.
    """

    consecutivo = db.Column(db.Integer, primary_key=True)
    cod_dist = db.Column(db.Integer)
    direccion = db.Column(db.String)
    fecha = db.Column(db.Date)

    def __init__(self, consecutivo, cod_dist, direccion, fecha):
        self.consecutivo = consecutivo
        self.cod_dist = cod_dist
        self.direccion = direccion
        self.fecha = fecha


@app.errorhandler(Exception)
def server_error(err):
    """
    Maneja los errores que puedan ocurrir en el servidor y retorna error 500.

    Retorna
    -------
    tuple
        Tupla que contiene el mensaje de error y el código de error 500.
    """

    app.logger.exception(err)
    return err, 500


@app.route("/", methods=["GET"])
def home():
    """
    Método de prueba para verificar que el servicio esté levantado.
    Ruta: /

    Retorna
    -------
    HTTP Response
        Respuesta que contiene el status 200 y un mensaje de éxito.
    """

    return Response("Servicio web funcionando correctamente.", status=200)


@app.route("/denuncia911", methods=["POST"])
def agregar_datos_911():
    """
    Carga los datos de las denuncias en la base de datos a partir de los parámetros suministrados.
    Espera un arreglo de denuncias en el formato {"consecutivo": A, "cod_dist": B, "direccion": C, "fecha": D},
    donde los valores para los parámetros son:
        - A: Entero, mayor que 0, único.
        - B: Entero, de acuerdo a la lista oficial de distritos del [INEC](https://www.inec.cr/sites/default/files/documentos/inec_institucional/metodologias/documentos_metodologicos/3_clasificacion_codigos_geograficos.pdf).
        - C: Hilera, máximo 500 caracteres.
        - D: Hilera, fecha en formato YYYY-MM-DD.
    Las denuncias se muestran por distrito y por fecha, agrupadas por cantidad, en el dashboard del mapa en el recuadro "Denuncias".

    En caso de ocurrir un error en el procesamiento, enviará un correo al administrador notificando el error, y guardará el registro de eventos en el servidor.

    Retorna
    -------
    HTTP Response
        Respuesta que contiene el status 200 y un mensaje de éxito en caso de no haber problemas, o el status 401 y un mensaje de error si la petición no fue autorizada.
    """

    try:
        token = request.headers["Authorization"]
        if token == TOKEN_DEFINED:
            request_data = request.json
            for i in request_data:
                denuncia = denuncia_911(
                    i["consecutivo"], i["cod_dist"], i["direccion"], i["fecha"]
                )
                db.session.add(denuncia)
                db.session.commit()

            return Response("Datos insertados correctamente", status=200)
        return Response("Incorrect Token", status=401)

    except Exception as err:
        noti = Notificador()
        noti.notificar(str(err))


if __name__ == "__main__":
    app.run(host="163.178.101.94", port=8443)
