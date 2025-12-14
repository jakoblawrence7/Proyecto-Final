from tkinter import *
from tkinter import messagebox, simpledialog

# ====== IMPORTS AGREGADOS PARA CONEXIÓN EN RED ======
import socket        # Permite comunicación entre computadoras
import threading     # Evita que Tkinter se congele al usar sockets

# ====== VARIABLES DE RED ======
conexion = None      # Socket de comunicación
es_servidor = False  # Indica si esta PC crea la partida
mi_turno = False     # Controla si el jugador puede jugar
PUERTO = 5000        # Puerto fijo para LAN

# ====== FUNCIÓN PARA OBTENER IP LOCAL DEL SERVIDOR ======
def obtener_ip_local():
    """
    Obtiene la IP local real del equipo para mostrarla al cliente.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    s.close()
    return ip

# ====== INICIAR SERVIDOR ======
def iniciar_servidor():
    """
    Configura el programa como servidor.
    El servidor inicia el juego y espera al cliente.
    """
    global es_servidor, mi_turno
    es_servidor = True
    mi_turno = True  # El servidor comienza

    ip = obtener_ip_local()
    messagebox.showinfo(
        "Servidor",
        f"Servidor iniciado\nIP: {ip}\nPuerto: {PUERTO}\n\nComparte esta IP con el cliente"
    )

    # Se espera al cliente en un hilo separado
    threading.Thread(target=esperar_cliente, daemon=True).start()

# ====== ESPERAR CONEXIÓN DEL CLIENTE ======
def esperar_cliente():
    """
    Espera la conexión del cliente sin bloquear Tkinter.
    """
    global conexion
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("0.0.0.0", PUERTO))
    servidor.listen(1)

    conexion, addr = servidor.accept()

    tablero.after(
        0,
        lambda: messagebox.showinfo(
            "Conectado",
            f"Cliente conectado desde {addr}"
        )
    )

    threading.Thread(target=escuchar_jugadas, daemon=True).start()

# ====== INICIAR CLIENTE ======
def iniciar_cliente():
    """
    Configura el programa como cliente y se conecta al servidor.
    """
    global conexion, es_servidor, mi_turno
    es_servidor = False
    mi_turno = False  # El cliente espera su turno

    ip = simpledialog.askstring("Cliente", "Ingresa la IP del servidor:")

    try:
        conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexion.connect((ip, PUERTO))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar\n{e}")
        return

    threading.Thread(target=escuchar_jugadas, daemon=True).start()

# ====== ENVÍO DE JUGADAS ======
def enviar_jugada(i):
    """
    Envía el índice del botón presionado al otro jugador.
    """
    try:
        conexion.send(str(i).encode())
    except:
        pass

# ====== RECEPCIÓN DE JUGADAS ======
def escuchar_jugadas():
    """
    Escucha jugadas del otro jugador sin bloquear la interfaz.
    """
    global mi_turno
    while True:
        try:
            data = conexion.recv(1024)
            if not data:
                break
            i = int(data.decode())
            tablero.after(0, lambda i=i: ejecutar_jugada_remota(i))
            mi_turno = True
        except:
            break

# ====== EJECUTA LA JUGADA RECIBIDA ======
def ejecutar_jugada_remota(i):
    """
    Ejecuta la jugada recibida reutilizando la misma lógica del juego.
    """
    botonClick(i, remoto=True)

# ======================================================
# ================= LÓGICA ORIGINAL ====================
# ======================================================

def crearBoton(valor,i):
    return Button(tablero,text=valor,width=5,height=1,font=("Helvetica",15),
                  command=lambda:botonClick(i))

def botonClick(i, remoto=False):
    """
    remoto = True si la jugada viene desde la red
    """
    global jugador,jugadas,X,Y,Z,g,mi_turno

    # ====== CONTROL DE TURNOS (CAMBIO) ======
    if not remoto and not mi_turno:
        return

    Z=int(i/16)
    y=i%16
    Y=int(y/4)
    X=y%4

    if g:
        return

    if not jugadas[Z][Y][X]:
        if jugador==0:
            texto='X'
            jugadas[Z][Y][X]=-1
            botones[i].config(text=texto,fg='blue')
        else:
            texto='O'
            jugadas[Z][Y][X]=1
            botones[i].config(text=texto,fg='red')

        # ====== ENVÍO DE JUGADA SOLO SI ES LOCAL ======
        if not remoto:
            enviar_jugada(i)
            mi_turno = False

        if horizontal() or vertical() or profundidad():
            ganador()
            return

        jugador = not jugador
        Label(tablero,text='Jugador '+str(jugador+1),
              font='arial 20',fg='green').place(x=500,y=620)

def ganador():
    global g
    g=1
    Label(tablero,text='GANADOR',font='arial 20',fg='blue').place(x=300,y=5)

def horizontal():
    return abs(sum(jugadas[Z][Y])) == 4

def vertical():
    return abs(sum(jugadas[Z][y][X] for y in range(4))) == 4

def profundidad():
    return abs(sum(jugadas[z][Y][X] for z in range(4))) == 4

def inicio():
    global jugador,g,mi_turno
    for z in range(4):
        for y in range(4):
            for x in range(4):
                jugadas[z][y][x]=0
                botones[z*16+y*4+x].config(text='',bg='white')
    jugador = g = 0

    # ====== EL SERVIDOR EMPIEZA ======
    mi_turno = es_servidor

# ===================== INTERFAZ =====================

jugadas = [[[0]*4 for _ in range(4)] for _ in range(4)]
botones=[]
g=0

tablero=Tk()
tablero.title('Tic Tac Toe 3D - Red LAN')
tablero.geometry("1040x720+100+5")
tablero.resizable(0,0)

for b in range(64):
    botones.append(crearBoton(' ',b))

contador=0
for z in range(3,-1,-1):
    for y in range(4):
        for x in range(4):
            botones[contador].grid(row=y+z*4,column=x+(3-z)*4)
            contador+=1

# ====== SELECCIÓN DE MODO (CAMBIO) ======
modo = messagebox.askyesno(
    "Modo de juego",
    "¿Deseas crear la partida?\nSí = Servidor | No = Cliente"
)

if modo:
    iniciar_servidor()
else:
    iniciar_cliente()

inicio()
tablero.mainloop()
