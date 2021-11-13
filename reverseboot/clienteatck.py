import socket
import sys


FIN_COMANDO = b'#00#'

def ver_lista(lista_clientes):
    x=1
    for cliente in lista_clientes:
        print('cliente %s :' % x)
        print(cliente)
        x+=1

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
    Espera la respuesta del servidor y la regresa
    comando viene como str
    """
    comando = comando.encode('utf-8') # convertir a binario
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
    Función con la interfaz de usuario
    """
    print('Para enviar un comando a un servidor debe poner el comando seguido de una coma y el numero de servidor: ls,1 \n Usa el comando "ver" para ver la lista de clientes') 
    comando = ''
    while comando != 'exit': 
        comando = input('$> ') # lee un str no binario
        respuesta = mandar_comando(comando, socket)
        desplegar_salida_comando(respuesta)
    socket.close()

#------------------------------------------------------------------------

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
    leer_comandos(socket)