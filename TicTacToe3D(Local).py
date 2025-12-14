from tkinter import *
from tkinter import messagebox, simpledialog
import socket
import threading

# ===================== RED =====================
conexion = None
es_servidor = False
mi_turno = False

PUERTO = 5000

def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    s.close()
    return ip

def iniciar_servidor():
    global es_servidor, mi_turno
    es_servidor = True
    mi_turno = True

    ip = obtener_ip_local()
    messagebox.showinfo(
        "Servidor",
        f"Servidor iniciado\nIP: {ip}\nPuerto: {PUERTO}\n\nComparte esta IP con el cliente"
    )

    threading.Thread(target=esperar_cliente, daemon=True).start()

def esperar_cliente():
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

def iniciar_cliente():
    global conexion, es_servidor, mi_turno
    es_servidor = False
    mi_turno = False

    ip = simpledialog.askstring(
        "Cliente",
        "Ingresa la IP del servidor:"
    )

    try:
        conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexion.connect((ip, PUERTO))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar\n{e}")
        return

    threading.Thread(target=escuchar_jugadas, daemon=True).start()

def enviar_jugada(i):
    try:
        conexion.send(str(i).encode())
    except:
        pass

def escuchar_jugadas():
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

def ejecutar_jugada_remota(i):
    botonClick(i, remoto=True)

# ===================== JUEGO =====================

def crearBoton(valor,i):
    return Button(
        tablero,
        text=valor,
        width=5,
        height=1,
        font=("Helvetica",15),
        command=lambda: botonClick(i)
    )

def botonClick(i, remoto=False):
    global jugador,jugadas,X,Y,Z,g,mi_turno        

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
            texto = 'X'
            jugadas[Z][Y][X]=-1
            botones[i].config(text=texto, fg='blue')
        else:
            texto = 'O'
            jugadas[Z][Y][X]=1
            botones[i].config(text=texto, fg='red')

        if not remoto:
            enviar_jugada(i)
            mi_turno = False

        if horizontal() or vertical() or profundidad():
            ganador()
            return

        jugador = not jugador
        Label(
            tablero,
            text='Jugador '+str(jugador+1),
            font='arial 20',
            fg='green'
        ).place(x=500, y=620)

def ganador():
    global g
    g=1
    Label(
        tablero,
        text='GANADOR',
        font='arial 20',
        fg='blue'
    ).place(x=300, y=5)

def horizontal():
    return abs(sum(jugadas[Z][Y])) == 4

def vertical():
    return abs(sum(jugadas[Z][y][X] for y in range(4))) == 4

def profundidad():
    return abs(sum(jugadas[z][Y][X] for z in range(4))) == 4

def inicio():
    global jugador, g, mi_turno
    for z in range(4):
        for y in range(4):
            for x in range(4):
                jugadas[z][y][x]=0
                botones[z*16+y*4+x].config(text='',bg='white')

    jugador = g = 0
    mi_turno = es_servidor

# ===================== INTERFAZ =====================

jugadas = [[[0]*4 for _ in range(4)] for _ in range(4)]
botones=[]
g=0

tablero=Tk()
tablero.title('Tic Tac Toe 3D - Red LAN')
tablero.geometry("1040x720+100+5")
tablero.resizable(0, 0)

for b in range(64):
    botones.append(crearBoton(' ',b))

contador=0
for z in range(3,-1,-1):
    for y in range(4):
        for x in range(4):
            botones[contador].grid(row=y+z*4,column=x+(3-z)*4)
            contador+=1

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
