from tkinter import *
from tkinter import messagebox, simpledialog
import socket
import threading

# ===================== RED =====================
conexion = None
es_servidor = False
mi_turno = False

def iniciar_servidor():
    global conexion, es_servidor, mi_turno
    es_servidor = True
    mi_turno = True

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("0.0.0.0", 5000))
    servidor.listen(1)

    messagebox.showinfo("Servidor", "Esperando al otro jugador...")
    conexion, addr = servidor.accept()
    messagebox.showinfo("Conectado", f"Jugador conectado desde {addr}")

    threading.Thread(target=escuchar_jugadas, daemon=True).start()

def iniciar_cliente():
    global conexion, es_servidor, mi_turno
    es_servidor = False
    mi_turno = False

    ip = simpledialog.askstring("Cliente", "IP del servidor:")
    conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexion.connect((ip, 5000))

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
    botonClick(i)

# ===================== JUEGO =====================

def crearBoton(valor,i):
    return Button(tablero,text=valor,width=5,height=1,font=("Helvetica",15),
                  command=lambda:botonClick(i))

def seguir_o_finalizar():
    global g
    resp = messagebox.askyesno("FINALIZAR", "¿Quieres continuar?")
    if resp:
        if g:
            inicio()
    else:
        tablero.destroy()
    return resp

def botonClick(i):
    global jugador,jugadas,X,Y,Z,g,mi_turno        

    if not mi_turno:
        return

    Z=int(i/16)
    y=i%16
    Y=int(y/4)
    X=y%4

    if g:
        seguir_o_finalizar()
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

        enviar_jugada(i)
        mi_turno = False

        if horizontal() or vertical() or profundidad():
            ganador()
            return

        jugador = not jugador
        texto=Label(tablero, text='Jugador '+str(jugador+1),font='arial, 20', fg='green')
        texto.place(x=500, y=620)
    else:
        texto=Label(tablero, text='Jugada Inválida ',font='arial, 20', fg='green')
        texto.place(x=300, y=5)

def ganador():
    global jugador,g
    texto=Label(tablero,text='Jugador '+str(jugador+1)+' GANO',font='arial, 20', fg='blue')
    texto.place(x=300, y=5)
    g=1

def horizontal():
    s=0
    for x in range(4):
        s+=jugadas[Z][Y][x]
    return abs(s)==4

def vertical():
    s=0
    for y in range(4):
        s+=jugadas[Z][y][X]
    return abs(s)==4

def profundidad():
    s=0
    for z in range(4):
        s+=jugadas[z][Y][X]
    return abs(s)==4

def inicio():
    global jugadas, jugador, g, mi_turno
    for z in range(4):
        for y in range(4):
            for x in range(4):
                jugadas[z][y][x]=0
                botones[z*16+y*4+x].config(text='',bg='white')
    g = jugador = 0
    mi_turno = es_servidor
    texto=Label(tablero, text='Jugador '+str(jugador+1),font='arial, 20', fg='green')
    texto.place(x=500, y=620)

# ===================== INTERFAZ =====================

jugadas = [[[0]*4 for _ in range(4)] for _ in range(4)]
botones=[]
g=0

tablero=Tk()
tablero.title('Tic Tac Toe 3D')
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

botonexit = Button(tablero,text='Exit',width=5,height=1,font=("Helvetica",15),
                   command=seguir_o_finalizar)
botonexit.grid(row=0,column=10)

tablero.mainloop()
