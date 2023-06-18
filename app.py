import json
import smtplib
import requests
import time
from flask import Flask

app = Flask(__name__)

# Configuración del servidor SMTP (correo saliente)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SMTP_USERNAME = 'jrosadointriago@gmail.com'
SMTP_PASSWORD = 'njuhafcaifohujuc'

# Direcciones de correo electrónico
SENDER_EMAIL = 'jrosadointriago@gmail.com'
RECIPIENT_EMAIL = 'jrosadointriago@gmail.com'

# URL de la API
API_URL = 'http://localhost:3000/estadoFirma'

# Valor a monitorear en la respuesta de la API
VALOR_MONITOREADO = 'Estado'

# Almacenamiento del valor anterior
VALOR_ANTERIOR = None

def enviar_correo_electronico(cambio):
    subject = 'Cambio detectado en la API'
    body = f'El valor "{VALOR_MONITOREADO}" ha cambiado. Nuevo valor: {cambio}'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message)

def monitorear_api():
    global VALOR_ANTERIOR

    response = requests.get(API_URL)
    data = response.json()
    valor_actual = data[0][VALOR_MONITOREADO]

    if VALOR_ANTERIOR is not None and valor_actual != VALOR_ANTERIOR:
        enviar_correo_electronico(valor_actual)

    VALOR_ANTERIOR = valor_actual

# Ruta de la página de inicio
@app.route('/')
def index():
    return 'Servicio de monitoreo activo'

# Ruta para iniciar el monitoreo
@app.route('/iniciar_monitoreo')
def iniciar_monitoreo():
    while True:
        monitorear_api()
        # Pausa de tiempo entre cada verificación (por ejemplo, cada 5 minutos)
        time.sleep(300)

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run()