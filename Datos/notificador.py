from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from datetime import datetime
import smtplib

class Notificador:

    def obtener_contactos(self, filename="/home/odd/plataformacovid19/Datos/emailConf/direcciones.txt"):
        nombres = []
        correos = []
        with open(filename, mode='r', encoding='utf-8') as archivo_contactos:
            for contacto in archivo_contactos:
                nombres.append(contacto.split(' ')[0])
                correos.append(contacto.split(' ')[1])
        return nombres, correos

    def obtener_plantilla(self, filename="/home/odd/plataformacovid19/Datos/emailConf/plantilla.txt"):
        with open(filename, 'r', encoding='utf-8') as archivo_plantilla:
            contenido = archivo_plantilla.read()
        return Template(contenido)

    def obtener_credenciales(self, filename="/home/odd/plataformacovid19/Datos/emailConf/credenciales.txt"):
        usuario = ''
        contrasena = ''
        with open(filename, 'rb') as archivo_credenciales:
            user = archivo_credenciales.readline()
            passwd = archivo_credenciales.readline()
            llave = archivo_credenciales.readline()
            f = Fernet(llave)
            usuario = f.decrypt(user)
            contrasena = f.decrypt(passwd)
        return usuario.decode('utf-8'), contrasena.decode('utf-8')

    def obtener_configuracion(self, filename="/home/odd/plataformacovid19/Datos/emailConf/configuracion.txt"):
        host = ''
        port = 0
        with open(filename, 'r', encoding='utf-8') as archivo_config:
            linea = archivo_config.readline()
            host = str(linea.split(' ')[0])
            port = int(linea.split(' ')[1])
        return host, port

    def notificar(self, error):
        usuario, contrasena = self.obtener_credenciales()
        host, port = self.obtener_configuracion()
        s = smtplib.SMTP(host=host, port=port)
        s.starttls()
        s.login(usuario, contrasena)

        nombres, correos = self.obtener_contactos()
        plantilla = self.obtener_plantilla()

        for nombre, correo in zip(nombres, correos):
            msg = MIMEMultipart()

            mensaje = plantilla.substitute(NOMBRE=nombre, FECHA=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), ERROR=error)

            msg['From'] = usuario
            msg['To'] = correo
            msg['Subject'] = 'Notificación COVID-19'

            msg.attach(MIMEText(mensaje, 'plain'))

            s.send_message(msg)

            del msg