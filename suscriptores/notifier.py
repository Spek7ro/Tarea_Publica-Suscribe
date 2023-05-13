##!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: notifier.py
# Capitulo: Estilo Publica-Suscribe
# Autor(es): Perla Velasco & Yonathan Mtz. & Jorge Solís
# Version: 3.0.0 Marzo 2022
# Descripción:
#
#   Esta clase define el suscriptor que recibirá mensajes desde el distribuidor de mensajes
#   y lo notificará a un(a) enfermero(a) én particular para la atención del adulto mayor en
#   cuestión
#
#   Este archivo también define el punto de ejecución del Suscriptor
#
#   A continuación se describen los métodos que se implementaron en esta clase:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |       __init__()       |  - self: definición de   |  - constructor de la  |
#           |                        |    la instancia de la    |    clase              |
#           |                        |    clase                 |                       |
#           +------------------------+--------------------------+-----------------------+
#           |       suscribe()       |  - self: definición de   |  - inicializa el      |
#           |                        |    la instancia de la    |    proceso de         |
#           |                        |    clase                 |    monitoreo de       |
#           |                        |                          |    signos vitales     |
#           +------------------------+--------------------------+-----------------------+
#           |        consume()       |  - self: definición de   |  - realiza la         |
#           |                        |    la instancia de la    |    suscripción en el  |
#           |                        |    clase                 |    distribuidor de    |
#           |                        |  - queue: ruta a la que  |    mensajes para      |
#           |                        |    el suscriptor está    |    comenzar a recibir |
#           |                        |    interesado en recibir |    mensajes           |
#           |                        |    mensajes              |                       |
#           |                        |  - callback: accion a    |                       |
#           |                        |    ejecutar al recibir   |                       |
#           |                        |    el mensaje desde el   |                       |
#           |                        |    distribuidor de       |                       |
#           |                        |    mensajes              |                       |
#           +------------------------+--------------------------+-----------------------+
#           |       callback()       |  - self: definición de   |  - envía a través de  |
#           |                        |    la instancia de la    |    telegram los datos |
#           |                        |    clase                 |    del adulto mayor   |
#           |                        |  - ch: canal de          |    recibidos desde el |
#           |                        |    comunicación entre el |    distribuidor de    |
#           |                        |    suscriptor y el       |    mensajes           |
#           |                        |    distribuidor de       |                       |
#           |                        |    mensajes [propio de   |                       |
#           |                        |    RabbitMQ]             |                       |
#           |                        |  - method: método de     |                       |
#           |                        |    conexión utilizado en |                       |
#           |                        |    la suscripción        |                       |
#           |                        |    [propio de RabbitMQ]  |                       |
#           |                        |  - properties:           |                       |
#           |                        |    propiedades de la     |                       |
#           |                        |    conexión [propio de   |                       |
#           |                        |    RabbitMQ]             |                       |
#           |                        |  - body: contenido del   |                       |
#           |                        |    mensaje recibido      |                       |
#           +------------------------+--------------------------+-----------------------+
#
#-------------------------------------------------------------------------
import json, time, pika, sys
import telepot
import stomp

class MyListener(object):
  
  def __init__(self, conn):
    self.conn = conn
    self.count = 0
    self.start = time.time()
  
  def on_error(self, message):
    print('received an error %s' % message)

  def on_message(self, message):
    print("enviando notificación de signos vitales...")
    if notifier.token and notifier.chat_id:
        data = json.loads(message.body)
        message = f"ADVERTENCIA!!!\n[{data['wearable']['date']}]: asistir al paciente {data['name']} {data['last_name']}...\nssn: {data['ssn']}, edad: {data['age']}, temperatura: {round(data['wearable']['temperature'], 1)}, ritmo cardiaco: {data['wearable']['heart_rate']}, presión arterial: {data['wearable']['blood_pressure']}, dispositivo: {data['wearable']['id']}"
        bot = telepot.Bot(self.token)
        bot.sendMessage(self.chat_id, message)
    time.sleep(1)

    #para cuando quieramos cerrar la conexion
    if message == "SHUTDOWN":
    
      diff = time.time() - self.start
      print("Recibido %s en %f Segundos" % (self.count, diff))
      self.conn.disconnect()
      sys.exit(0)
      
    else:
      if self.count==0:
        self.start = time.time()
        
      self.count += 1
      if self.count % 1000 == 0:
         print("Recibido %s mensajes." % self.count)

class Notifier:

    def __init__(self):
        self.topic = "notifier"
        self.token = ""
        self.chat_id = ""

    def suscribe(self):
        print("Inicio de gestión de notificaciones...")
        print()
        
        conn = stomp.Connection()#realizamos la conexion con activeMQ
        conn.set_listener('', MyListener(conn))#creamos el escucha
        conn.connect('admin', 'password', wait=True)#pasamos el usuario y la contraseña para conectarnos y nos conectamos     
        conn.subscribe(destination=self.topic, id=1, ack='auto')#agregamos un suscriptor

        print("Esperando mensajes...")
        while 1: 
            time.sleep(10)



if __name__ == '__main__':
    notifier = Notifier()
    notifier.suscribe()