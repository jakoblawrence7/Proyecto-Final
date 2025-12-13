from tkinter import *
from tkinter import messagebox

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
    global jugador,jugadas,X,Y,Z,g        
        
    Z=int(i/16)
    y=i%16
    Y=int(y/4)
    X=y%4
    print('Z='+str(Z)+' Y='+str(Y)+' X='+str(X))
    if g:
        seguir_o_finalizar()
        return
    if not jugadas[Z][Y][X]:
        texto=Label(tablero, text='                          ',font='arial, 20', fg='gray') # white
        texto.place(x=300, y=5)
        if jugador==0:
            texto = 'X'
            jugadas[Z][Y][X]=-1
            botones[i].config(text=texto, font='arial 15',fg='blue')
        else:
            texto = 'O'
            jugadas[Z][Y][X]=1
            botones[i].config(text=texto, font='arial 15',fg='red')
        if horizontal():   #La Z y Y no varia, x => 0 -> 3 en letras minusculas
            ganador()
            for z in range(4):
                botones[z*16+(3-z)*4+z].config(text=texto, font='arial 15',fg='yellow',bg='red')
            return
        if vertical():   #La Z y X no varia, y +> 0 -> 3 en letras minusculas
            ganador()
            for z in range(4):
                botones[Z*16+y*4+X].config(text=texto, font='arial 15',fg='yellow',bg='red')
            return
        if profundidad():    #La Y y X no varia, z => 0 -> 3 en letras minusculas
            ganador()
            for z in range(4):
                botones[z*16+(3-z)*4+z].config(text=texto, font='arial 15',fg='yellow',bg='red')
            return
        if not g:
            jugador = not jugador
            texto=Label(tablero, text='Jugador '+str(jugador+1),font='arial, 20', fg='green')
            texto.place(x=500, y=620)
    else:
        texto=Label(tablero, text='Jugada Inválida ',font='arial, 20', fg='green')
        texto.place(x=300, y=5)
#    print(jugadas)

def ganador():
    global jugador,g
    texto=Label(tablero,text='Jugador '+str(jugador+1)+' GANO',font='arial, 20', fg='blue')
    texto.place(x=300, y=5)
    g=1

def horizontal():
    global Y,Z
    s=0
    for x in range(4):
        s+=jugadas[Z][Y][x]
    if s<4 and s>-4:
        return False
    return True

def vertical():
    global Z,X
    s=0
    for y in range(4):
        s+=jugadas[Z][y][X]
    print(str(s)+'v')
    if s<4 and s>-4:
        return False
    return True

def profundidad():
    global X,Y
    s=0
    for z in range(4):
        s+=jugadas[z][Y][X]
    print(str(s)+'p')
    if s<4 and s>-4:
        return False
    return True


def inicio():
    global jugadas, X, Y, Z, jugador, g
    for z in range(4):
        for y in range(4):
            for x in range(4):
                jugadas[z][y][x]=0
                botones[z*16+y*4+x].config(text='',font='arial 15',fg='blue',bg='white')
    X = Y= Z= 0
    g = jugador = 0
    texto=Label(tablero, text='Jugador '+str(jugador+1),font='arial, 20', fg='green')
    texto.place(x=500, y=620)

jugadas = [[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
           [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
           [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
           [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]] 
botones=[]
g=0

tablero=Tk()
tablero.title('Tic Tac Toe 3D')
tablero.geometry("1040x720+100+5")
tablero.resizable(0, 0)

for b in range(64):
    botones.append(crearBoton(' ',b))        
# for z in range(4):
#     for y in range(4):
#         for x in range(4):
#             botones[z*16+y*4+x].grid(row=y+z*4,column=x+z*4)                       
contador=0
for z in range(3,-1,-1):
    for y in range(4):
        for x in range(4):
            botones[contador].grid(row=y+z*4,column=x+(3-z)*4)
            contador+=1

inicio()
botonexit = Button(tablero,text='Exit',width=5,height=1,font=("Helvetica",15),
                   command=seguir_o_finalizar)
botonexit.grid(row=0,column=10)

tablero.mainloop()   