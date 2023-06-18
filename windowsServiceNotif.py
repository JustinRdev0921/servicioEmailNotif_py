import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import time
import json
import smtplib
import requests

# Configuración del servidor SMTP (correo saliente)
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
SMTP_USERNAME = 'jrosado@ecuacopia.com'
SMTP_PASSWORD = 'Kvc3sura17-'

# Direcciones de correo electrónico
SENDER_EMAIL = 'jrosado@ecuacopia.com'
RECIPIENT_EMAIL = 'jrosado@ecuacopia.com'

# URL de la API
API_URL = 'http://localhost:3000/estadoFirma'

# Valor a monitorear en la respuesta de la API
VALOR_MONITOREADO = 'En procesooo'

# Almacenamiento del valor anterior
VALOR_ANTERIOR = None

class MonitoreoServicio(win32serviceutil.ServiceFramework):
    _svc_name_ = 'MonitoreoServicio'
    _svc_display_name_ = 'Servicio de Monitoreo envio email'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        while self.is_running:
            self.monitorear_api()
            # Pausa de tiempo entre cada verificación (por ejemplo, cada 5 minutos)
            time.sleep(300)

    def enviar_correo_electronico(self, cambio):
        subject = 'Nuevo estado de la firma electronica'
        body = f'El estado de la firma es {cambio}'

        message = f'Subject: {subject}\n\n{body}'

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message)

    def monitorear_api(self):
        global VALOR_ANTERIOR

        response = requests.get(API_URL)
        data = response.json()
        valor_actual = data[VALOR_MONITOREADO]

        if VALOR_ANTERIOR is not None and valor_actual != VALOR_ANTERIOR:
            self.enviar_correo_electronico(valor_actual)

        VALOR_ANTERIOR = valor_actual

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MonitoreoServicio)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MonitoreoServicio)
