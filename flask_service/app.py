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


class denuncia_911(db.Model):
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
    app.logger.exception(err)
    return err, 500


@app.route("/", methods=["GET"])
def home():
    return Response("Servicio web funcionando correctamente.", status=200)


@app.route("/denuncia911", methods=["POST"])
def agregar_datos_911():
    try:
        token = request.headers["Authorization"]
        print("Received request!")
        if token == TOKEN_DEFINED:
            request_data = request.json
            print("Authenticated")
            print(request_data)
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
