from tkinter import *
from tkinter import messagebox, simpledialog


# =============== IMPORTS DE RED ======================

import socket        # Comunicación entre computadoras
import threading     # Evita que Tkinter se congele


# =============== VARIABLES DE RED ====================

conexion = None
es_servidor = False
mi_turno = False
PUERTO = 5000        # Mismo puerto para LAN / WAN


# ========== FUNCIÓN PARA MOSTRAR IPs =================

def mostrar_ips_locales():
    """
    Muestra posibles IPs del equipo (LAN / ZeroTier).
    Ayuda al usuario a identificar la IP correcta.
    """
    hostname = socket.gethostname()
    ips = socket.getaddrinfo(hostname, None)

    lista_ips = set()
    for ip in ips:
        direccion = ip[4][0]
        if direccion.startswith("10.") or direccion.startswith("192."):
            lista_ips.add(direccion)

    return "\n".join(lista_ips) if lista_ips else "No detectadas"


# ================= INICIAR SERVIDOR ==================

def iniciar_servidor():
    """
    Configura el programa como servidor (WAN).
    El servidor espera al cliente usando IP ZeroTier.
    """
    global es_servidor, mi_turno
    es_servidor = True
    mi_turno = True  # El servidor comienza

    ips = mostrar_ips_locales()

    messagebox.showinfo(
        "Modo WAN - Servidor",
        "Servidor iniciado en MODO WAN (ZeroTier)\n\n"
        "1. Abre ZeroTier\n"
        "2. Copia la IP virtual del servidor\n"
        "3. Comparte esa IP con el cliente\n\n"
        f"IPs detectadas en este equipo:\n{ips}\n\n"
        f"Puerto: {PUERTO}"
    )

    threading.Thread(target=esperar_cliente, daemon=True).start()


# ============== ESPERAR AL CLIENTE ===================

def esperar_cliente():
    """
    Espera la conexión del cliente sin bloquear la interfaz.
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
            f"Cliente conectado desde:\n{addr}"
        )
    )

    threading.Thread(target=escuchar_jugadas, daemon=True).start()


# ================= INICIAR CLIENTE ===================

def iniciar_cliente():
    """
    Configura el programa como cliente WAN.
    Solicita la IP ZeroTier del servidor.
    """
    global conexion, es_servidor, mi_turno
    es_servidor = False
    mi_turno = False

    messagebox.showinfo(
        "Modo WAN - Cliente",
        "Este modo permite jugar desde redes diferentes.\n\n"
        "Asegúrate de estar conectado a ZeroTier\n"
        "y de usar la IP virtual del servidor."
    )

    ip = simpledialog.askstring(
        "Cliente WAN",
        "Ingresa la IP ZeroTier del servidor:\n(Ejemplo: 10.xx.xx.xx)"
    )

    try:
        conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexion.connect((ip, PUERTO))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar\n{e}")
        return

    threading.Thread(target=escuchar_jugadas, daemon=True).start()


# ================= ENVÍO DE JUGADAS ==================

def enviar_jugada(i):
    """
    Envía la jugada al otro jugador.
    """
    try:
        conexion.send(str(i).encode())
    except:
        pass


# =============== RECEPCIÓN DE JUGADAS ================

def escuchar_jugadas():
    """
    Escucha jugadas del otro jugador sin congelar la UI.
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


# ========= EJECUTAR JUGADA REMOTA ====================

def ejecutar_jugada_remota(i):
    botonClick(i, remoto=True)


# ================= LÓGICA ORIGINAL ===================

def crearBoton(valor,i):
    return Button(tablero,text=valor,width=5,height=1,font=("Helvetica",15),
                  command=lambda:botonClick(i))

def botonClick(i, remoto=False):
    global jugador,jugadas,X,Y,Z,g,mi_turno

    # ===== CONTROL DE TURNOS =====
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
    mi_turno = es_servidor


# ================= INTERFAZ ==========================
jugadas = [[[0]*4 for _ in range(4)] for _ in range(4)]
botones=[]
g=0

tablero=Tk()
tablero.title('Tic Tac Toe 3D - WAN (ZeroTier)')
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


# ============ SELECCIÓN DE MODO ======================
modo = messagebox.askyesno(
    "Modo de juego",
    "¿Deseas crear la partida?\n\n"
    "Sí = Servidor\n"
    "No = Cliente"
)

if modo:
    iniciar_servidor()
else:
    iniciar_cliente()

inicio()
tablero.mainloop()
