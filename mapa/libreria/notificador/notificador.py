from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from datetime import datetime
import smtplib
import covid_project.settings as sysconf


class Notificador:
    """
    Clase utilizada para enviar notificaciones por correo electrónico.
    Necesita de cuatro archivos para funcionar, en la carpeta emailConf:
    - configuracion.txt: servidor SMTP y puerto en el formato <Servidor SMTP> <puerto>.txt
    - credenciales.txt: contiene las credenciales cifradas utilizando el algoritmo de cifrado simétrico Fernet.
        Las credenciales se guardan una por línea en el siguiente orden: usuario, contraseña, llave Fernet. La llave no está cifrada en el archivo.
    - direcciones.txt: destinatarios para la notificación por línea, en el formato <nombre> <correo>.
    - plantilla.txt: plantilla de la notificación a enviar.

    Atributos
    ---------
    cwd : str
        Ruta actual donde se está ejecutando el script

    Métodos
    -------
    obtener_contactos(filename=cwd + "/emailConf/direcciones.txt")
        Obtiene la lista de destinatarios para enviar la notificación.

    obtener_plantilla(filename=cwd + "/emailConf/plantilla.txt")
        Obtiene la plantilla para enviar la notificación.

    obtener_credenciales(filename=cwd + "/emailConf/credenciales.txt")
        Obtiene y desencripta las credenciales del servidor SMTP para enviar la notificación.

    obtener_configuracion(filename=cwd + "/emailConf/configuracion.txt")
        Obtiene la configuración del servidor SMTP para enviar la notificación.
    """

    # Cambiar ruta según el servidor.
    cwd = sysconf.BASE_DIR + "/mapa/libreria/notificador"

    def obtener_contactos(self, filename=cwd + "/emailConf/direcciones.txt"):
        """
        Obtiene la lista de destinatarios para enviar la notificación.

        Parámetros
        ----------
        filename : str
            Nombre y ruta del archivo donde están las direcciones de correo.

        Retorna
        -------
        Tuple
            Tupla que contiene la lista de nombres y sus respectivos correos.
        """

        nombres = []
        correos = []
        with open(filename, mode="r", encoding="utf-8") as archivo_contactos:
            for contacto in archivo_contactos:
                nombres.append(contacto.split(" ")[0])
                correos.append(contacto.split(" ")[1])
        return nombres, correos

    def obtener_plantilla(self, filename=cwd + "/emailConf/plantilla.txt"):
        """
        Obtiene la plantilla para enviar la notificación.

        Parámetros
        ----------
        filename : str
            Nombre y ruta del archivo que contiene la plantilla de la notificación.

        Retorna
        -------
        Template
            Plantilla para rellenar con los campos identificados.
        """

        with open(filename, "r", encoding="utf-8") as archivo_plantilla:
            contenido = archivo_plantilla.read()
        return Template(contenido)

    def obtener_credenciales(self, filename=cwd + "/emailConf/credenciales.txt"):
        """
        Obtiene y desencripta las credenciales del servidor SMTP para enviar la notificación.

        Parámetros
        ----------
        filename : str
            Nombre y ruta del archivo que contiene las credenciales cifradas y la llave de cifrado.

        Retorna
        -------
        Tuple
            Tupla que contiene el usuario y la contraseña descifrados.
        """

        usuario = ""
        contrasena = ""
        with open(filename, "rb") as archivo_credenciales:
            user = archivo_credenciales.readline()
            passwd = archivo_credenciales.readline()
            llave = archivo_credenciales.readline()
            f = Fernet(llave)
            usuario = f.decrypt(user)
            contrasena = f.decrypt(passwd)
        return usuario.decode("utf-8"), contrasena.decode("utf-8")

    def obtener_configuracion(self, filename=cwd + "/emailConf/configuracion.txt"):
        """
        Obtiene la configuración del servidor SMTP para enviar la notificación.

        Parámetros
        ----------
        filename : str
            Nombre y ruta del archivo que contiene la configuración del servidor SMTP.

        Retorna
        -------
        Tuple
            Tupla que contiene el host y puerto del servidor SMTP.
        """

        host = ""
        port = 0
        with open(filename, "r", encoding="utf-8") as archivo_config:
            linea = archivo_config.readline()
            host = str(linea.split(" ")[0])
            port = int(linea.split(" ")[1])
        return host, port

    def notificar(self, error):
        """
        Método principal que envía la notificación de error por correo, junto con la fecha y hora en la que ocurrió.

        Parámetros
        ----------
        error : str
            Error que debe ser notificado por correo.
        """

        usuario, contrasena = self.obtener_credenciales()
        host, port = self.obtener_configuracion()
        s = smtplib.SMTP(host=host, port=port)
        s.starttls()
        s.login(usuario, contrasena)

        nombres, correos = self.obtener_contactos()
        plantilla = self.obtener_plantilla()

        for nombre, correo in zip(nombres, correos):
            msg = MIMEMultipart()

            mensaje = plantilla.substitute(
                NOMBRE=nombre,
                FECHA=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                ERROR=error,
            )

            msg["From"] = usuario
            msg["To"] = correo
            msg["Subject"] = "Notificación COVID-19"

            msg.attach(MIMEText(mensaje, "plain"))

            s.send_message(msg)

            del msg
