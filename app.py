from flask import Flask,  render_template,flash,url_for
from flask import redirect, session, send_file, current_app, g,flash,url_for
from flask import request
from db import get_db, close_db
import json
import os
import utils
import functools
from re import X
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__)
app.secret_key = os.urandom( 24 )

sesion_ini=False
lista_platos=[]
lista_usuarios=[]
lista_deseos=[]
encontrado=None

@app.route('/', methods=['GET'])
def inicio():     ##si ya inició sesion muestre la de abajo, sino esta
    return render_template('inicio.html', sesion_ini=sesion_ini)

@app.route('/inicioI', methods=['GET','POST'])
def inicioInicida():
    global sesion_ini
    if(sesion_ini):
        return render_template('inicioIniciada.html',sesion_ini=sesion_ini)
    else:
        return redirect('/')

@app.route('/promos', methods=['GET'])
def promos():
    return render_template('promos.html')   

#####################################################3
@app.route('/registro', methods=['GET','POST'])
def registro():
    error=" "
    global sesion_ini
    try:
        if(request.method =="GET"):
            return render_template('registro.html')
        else: 
            nombre = request.form['nombre']
            apellido=request.form['apellido']
            Nombre= nombre + " "+ apellido
            correo= request.form['correo']
            contraseña=request.form['contraseña']
            telefono= request.form['telefono']
            direccion= request.form['direccion']
            rol="usuariof"
            db=get_db()
            if not utils.isPasswordValid(contraseña):
                error = 'La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres'
                flash( error )
                return render_template('registro.html',error=error )

            if not utils.isEmailValid(correo):
                error = 'Correo invalido'
                flash( error )
                return render_template('registro.html',error=error)
            
            query1='SELECT ID FROM USUARIO WHERE CORREO = ?'
            tupla1=(correo,)
            encontrado=db.execute(query1,tupla1).fetchone()
            
            if encontrado is not None:
                error = f"El correo {correo}  ya existe"
                flash( error )
                return render_template('registro.html', error=error)
            
            query2="INSERT INTO USUARIO(ROL,NOMBRE,CORREO,CONTRASEÑA,TELEFONO,DIRECCION) VALUES(?,?,?,?,?,?)"
            tupla2=(rol,Nombre,correo,generate_password_hash(contraseña),telefono,direccion)
            db.execute(query2,tupla2)
            db.commit()
            return redirect( '/login' )
    except Exception as e:
        print(e)
        return render_template('registro.html')
        


@app.route('/login', methods=['GET','POST'])
def login():
    global sesion_ini
    error=" "
    try:
        if(request.method =="GET"):
            return render_template('login.html')
        else: 
            global encontrado
            email = request.form['correo']
            contraseña = request.form['contraseña']
            db = get_db()
            error = None
            query3= 'SELECT * FROM USUARIO WHERE CORREO = ? '
            tupla3=(email,)
            encontrado=db.execute(query3,tupla3).fetchone()
            
            if encontrado is None:
                error= 'Usuario no existe'
                return render_template('login.html', error=error)
            else:
                #Validar contraseña hash            
                store_password = encontrado[4]
                result = check_password_hash(store_password, contraseña)
                if result is False:
                    error='Contraseña inválida'
                    return render_template('login.html', error=error)
                else: 
                    sesion_ini=True
                    session.clear()
                    session['user_id'] = encontrado[0]
                    print(session['user_id'])
                    close_db()
                    return redirect( '/')            
    except Exception as e:
        print(e)
        return render_template( 'login.html' )


@app.route('/logout', methods=['GET','POST'])
def logout():
    global sesion_ini
    sesion_ini=False
    session.clear()
    return redirect('/') #pag de inicio

def login_required(view):
    @functools.wraps( view )
    def wrapped_view(**kwargs):
        global encontrado
        if encontrado is None:
            return redirect( url_for( 'login' ) )

        return view( **kwargs )

    return wrapped_view    

@app.route('/perfil', methods=['GET','POST'])
@login_required
def perfil():
    global sesion_ini
    id=session['user_id']
    db = get_db()
    query4='SELECT * FROM USUARIO WHERE ID = ? '
    tupla4=(id,)
    encontrado=db.execute(query4,tupla4).fetchone()
    print(encontrado)
    rol=encontrado[1]
    nombre=encontrado[2]
    email=encontrado[3]
    telefono=encontrado[5]
    direccion=encontrado[6]
    foto=encontrado[7]
    if(rol=="usuariof"):
        return render_template('perfil.html', email=email,nombre=nombre,telefono=telefono,direccion=direccion,foto=foto,sesion_ini=sesion_ini) 
    elif(rol=="admin"):
        return render_template('admin.html', email=email,nombre=nombre,telefono=telefono,direccion=direccion,foto=foto,sesion_ini=sesion_ini)
    elif(rol=="superadmin"):
        return render_template('superadmin.html', email=email,nombre=nombre,telefono=telefono,direccion=direccion,foto=foto,sesion_ini=sesion_ini)
    else:
        return "Usuario no encontrado"

    
    
######################################################
@app.route('/menu',methods=['GET'])
def menu():
    global lista_platos
    db=get_db()
    if(request.method =="GET"):
            lista_platos=[]
            query5='SELECT * FROM PLATO'
            for row in db.execute(query5):
                lista_platos.append(row)
            print(lista_platos)
    return render_template('menu.html',sesion_ini=sesion_ini, lista_platos=lista_platos) 
@app.route('/menuIni',methods=['GET'])
@login_required
def menu2():
    global lista_platos
    global sesion_ini
    db=get_db()
    if(request.method =="GET"):
            lista_platos=[]
            query6='SELECT * FROM PLATO'
            for row in db.execute(query6):
                lista_platos.append(row)
            print(lista_platos)
    return render_template('menuIni.html',sesion_ini=sesion_ini, lista_platos=lista_platos) 

@app.route('/plato',methods=['GET','POST'])
def plato():
    db=get_db()
    global sesion_ini
    print(sesion_ini)
    if(request.method =="POST"):
        id=int(request.form['id'])
        query7='SELECT * FROM PLATO WHERE ID = ? '
        tupla7=(id,)
        encontrado=db.execute(query7,tupla7).fetchone()
        print(encontrado)
        nombre=encontrado[1]
        descripcion=encontrado[2]
        precio=encontrado[3]
        foto=encontrado[4]
        lista_comentario=[]
        query8='SELECT * FROM COMENTARIO, USUARIO WHERE COMENTARIO.USUARIO = USUARIO.ID AND COMENTARIO.PLATO = ? '
        tupla8=(id,)
        for row in db.execute(query8,tupla8):
            lista_comentario.append(row)
        print(lista_comentario)
        return render_template('plato1.html',sesion_ini=sesion_ini,id=id, nombre=nombre,descripcion=descripcion,precio=precio,foto=foto,lista_comentario=lista_comentario)
    else:return redirect('/menu')
    
#@app.route('/plato2',methods=['GET','POST'])
#def plato2():
    #lista_comentario=[]
#    db=get_db()
#    query10='SELECT * FROM COMENTARIO, USUARIO WHERE COMENTARIO.USUARIO = USUARIO.ID AND COMENTARIO.PLATO = ? '
#   tupla10=(2,)
#   for row in db.execute(query10,tupla10):
#        lista_comentario.append(row)
#    print(lista_comentario)
#    return render_template('plato2.html',sesion_ini=sesion_ini,lista_comentario=lista_comentario) 
#print@app.route('/plato3',methods=['GET','POST'])
#def plato3():
#    lista_comentario=[]
#    db=get_db()
#    query10='SELECT * FROM COMENTARIO, USUARIO WHERE COMENTARIO.USUARIO = USUARIO.ID AND COMENTARIO.PLATO = ? '
#    tupla10=(3,)
#    for row in db.execute(query10,tupla10):
#        lista_comentario.append(row)
#    print(lista_comentario)
#    return render_template('plato3.html',sesion_ini=sesion_ini,lista_comentario=lista_comentario)
######################################################   

@app.route('/lista',methods=['GET','POST'])
@login_required
def listaDeseos():
    global sesion_ini
    global lista_deseos
    id=session['user_id']
    db = get_db()
    if(sesion_ini==True):
        if(request.method =="GET"):
            query9='SELECT * FROM LISTAD, PLATO WHERE LISTAD.PLATO = PLATO.ID AND LISTAD.USUARIO = ? '
            tupla9= (id,)
            lista_deseos=[]
            for row in db.execute(query9,tupla9):
                lista_deseos.append(row)
            print(lista_deseos)
            return render_template('listaDeseos.html',lista_deseos=lista_deseos) 
        else:
            id_plato=int(request.form['id'])
            print(id)
            print(id_plato)
            query10='DELETE FROM LISTAD WHERE USUARIO=? AND PLATO =?'
            tupla10=(id, id_plato)
            db.execute(query10,tupla10)
            db.commit()
            return redirect('/lista')
    else:return redirect('/login')
    
@app.route('/agregar_lista',methods=['GET','POST'])
@login_required
def agregarListaDeseos():
    global sesion_ini
    global lista_deseos
    id=session['user_id']
    db = get_db()
    if(sesion_ini==True):
        if(request.method =="GET"):
            return render_template('listaDeseos.html',lista_deseos=lista_deseos) 
        else:
            id_plato=int(request.form['id'])
            #print(id)
            #print(id_plato)
            query11= "INSERT INTO LISTAD(USUARIO,PLATO) VALUES(?,?)"
            tupla11=(id,id_plato)
            db.execute(query11,tupla11)
            db.commit()
            return redirect('/lista')
    else:return redirect('/login')
    
@app.route('/mis_comentarios',methods=['GET','POST'])
@login_required
def comentariosRealizados():
    id=session['user_id']
    db=get_db()
    if(request.method =="GET"):
        lista_comentario=[]
        query12='SELECT * FROM COMENTARIO, PLATO WHERE COMENTARIO.PLATO = PLATO.ID AND COMENTARIO.USUARIO = ? '
        tupla12=(id,)
        for row in db.execute(query12,tupla12):
            lista_comentario.append(row)
        print(lista_comentario)
        return render_template('mis_comentarios.html',sesion_ini=sesion_ini,lista_comentario=lista_comentario) 
    else:
        id_plato=int(request.form['id'])
        print(id)
        print(id_plato)
        query13='DELETE FROM COMENTARIO WHERE USUARIO=? AND PLATO =?'
        tupla13=(id, id_plato)
        db.execute(query13,tupla13)
        db.commit()
        return redirect('/mis_comentarios')
    
@app.route('/historial', methods=['GET','POST'])
@login_required
def historialPedidos():
        return render_template('historialPedidos.html')

@app.route('/comentar_plato', methods=['GET','POST'])
@login_required
def comentarPlato():
    id=session['user_id']
    db=get_db()
    if(sesion_ini==True):
        if(request.method =="POST"):
            nombre=request.form['comen']
            comen=request.form['input']
            query14='SELECT ID FROM PLATO WHERE NOMBRE = ? '
            tupla14=(nombre,)
            encontrado=db.execute(query14,tupla14).fetchone()
            id_plato=encontrado[0]
            print(encontrado)
            #print(id_plato)
            query15= "INSERT INTO COMENTARIO(USUARIO,PLATO,COMENTARIO) VALUES(?,?,?)"
            tupla15=(id,id_plato,comen)
            db.execute(query15,tupla15)
            db.commit()
            return redirect('/mis_comentarios')
    else:return redirect('/login')

@app.route('/metodos_pago', methods=['GET','POST'])
@login_required
def metodosPago():
        return render_template('metodosPago.html')
    
@app.route('/carrito', methods=['GET','POST'])
@login_required
def carroCompras():
    db = get_db()
    id=session['user_id']
    if(sesion_ini==True):
        if(request.method =="GET"):
            carro=[]
            query16='SELECT * FROM CARRITO, PLATO WHERE CARRITO.PLATO = PLATO.ID AND CARRITO.USUARIO = ? '
            tupla16=(id,)
            for row in db.execute(query16,tupla16):
                carro.append(row)
            print("carro",carro)
            #print(carro[0][0])
            return render_template('carroCompras.html',carro=carro)
        else: 
            id_plato=int(request.form['id'])
            query17="INSERT INTO CARRITO(USUARIO,PLATO) VALUES(?,?)"
            tupla17=(id,id_plato)
            db.execute(query17,tupla17)
            db.commit()
            return redirect('/carrito')
    return redirect('/login')
@app.route('/eliminar_carrito', methods=['GET','POST'])
@login_required
def carroCompras2():
    db = get_db()
    id=session['user_id']
    if(request.method =="POST"):
        id_plato=int(request.form['id'])
        query17="DELETE FROM CARRITO WHERE USUARIO=? AND PLATO=?"
        tupla17=(id,id_plato)
        print(id,id_plato)
        db.execute(query17,tupla17)
        db.commit()
        return redirect('/carrito')
    return redirect('/carrito')
    
@app.route('/carrito/pedido', methods=['GET','POST'])
def realizarPedido():
        return render_template('realizarPedido.html')
#################################################################
@app.route('/resultado', methods=['GET','POST'])

#################################################################
@app.route('/admin', methods=['GET','POST'])
@login_required
def perfilAdmin():
    return render_template('admin.html') 

@app.route('/superadmin', methods=['GET','POST'])
@login_required
def perfilSadmin():
    return render_template('superadmin.html') 

@app.route('/c_contraseña', methods=['GET','POST'])
@login_required
def ccontraseña():
    id=session['user_id']
    if(request.method =="GET"):
        return render_template('c_contraseña.html') 
    else:
        query18= 'SELECT * FROM USUARIO WHERE ID = ? '
        tupla18=(id,)
        db=get_db()
        contraseña=request.form['contraseña']
        ncontraseña=request.form['ncontraseña']
        encontrado=db.execute(query18,tupla18).fetchone()
        print(encontrado)
        #if(encontrado[1]=="superadmin"):
            #if(encontrado[4]==contraseña):
                #query23='UPDATE USUARIO SET CONTRASEÑA=? WHERE ID=?'
                #tupla23=(generate_password_hash(ncontraseña),id)
                #db.execute(query23,tupla23)
                #db.commit()       
        store_password = encontrado[4]
        result = check_password_hash(store_password, contraseña)
        if result is True:
            query19='UPDATE USUARIO SET CONTRASEÑA=? WHERE ID=?'
            tupla19=(generate_password_hash(ncontraseña),id)
            db.execute(query19,tupla19)
            db.commit()
        else: return "Contraseña inválida"
    return redirect('/perfil') 

@app.route('/gestionPlato', methods=['GET','POST'])
@login_required
def gestionarPlato():
    global sesion_ini
    db = get_db()
    global lista_platos
    if(sesion_ini==True):
        if(request.method =="GET"):
            lista_platos=[]
            query20='SELECT * FROM PLATO'
            for row in db.execute(query20):
                lista_platos.append(row)
                #print(lista_platos)
            return render_template('gestionarPlato.html',lista_platos=lista_platos) 
        else:
            id=int(request.form['3'])
            #lon=len(lista_platos)-1
            query21='DELETE FROM PLATO WHERE ID =?'
            tupla21=(id,)
            db.execute(query21,tupla21)
            db.commit()
            #db.execute(
             #  "UPDATE SQLITE_SEQUENCE SET SEQ=? WHERE NAME='PLATO'",(lon,)
            #)
            #db.commit()
            #encontrado=[i for i in lista_platos if i[1]==id]
            #lista_platos.remove(encontrado[0])
            #print(lista_platos)
            return redirect('/gestionPlato')
    else:return redirect('/login')
        

@app.route('/gestionUsuario', methods=['GET','POST'])
@login_required
def gestionarUsuario():
    global sesion_ini
    db = get_db()
    global lista_usuarios
    if(sesion_ini==True):
        if(request.method =="GET"):
            lista_usuarios=[]
            query22='SELECT * FROM USUARIO'
            for row in db.execute(query22):
                lista_usuarios.append(row)
            return render_template('gestionarUsuario.html',lista_usuarios=lista_usuarios) 
        else:
            id=int(request.form['3'])
            #lon=len(lista_platos)-1
            query23='DELETE FROM USUARIO WHERE ID =?'
            tupla23=(id,)
            db.execute(query23,tupla23)
            db.commit()
            #db.execute(
             #  "UPDATE SQLITE_SEQUENCE SET SEQ=? WHERE NAME='PLATO'",(lon,)
            #)
            #db.commit()
            #encontrado=[i for i in lista_platos if i[1]==id]
            #lista_platos.remove(encontrado[0])
            #print(lista_platos)
            return redirect('/gestionUsuario')
    else:return redirect('/login')
@app.route('/gestion_usuariof', methods=['GET','POST'])
@login_required
def gestionarUsuariof():
    global sesion_ini
    db = get_db()
    global lista_usuarios
    if(sesion_ini==True):
        if(request.method =="GET"):
            lista_usuariosf=[]
            query24="SELECT * FROM USUARIO WHERE ROL='usuariof'"
            for row in db.execute(query24):
                lista_usuariosf.append(row)
            return render_template('gestionarUsuariosf.html',lista_usuariosf=lista_usuariosf) 
        else:
            id=int(request.form['3'])
            query25='DELETE FROM USUARIO WHERE ID =?'
            tupla25=(id,)
            db.execute(query25,tupla25)
            db.commit()
            return redirect('/gestion_usuariof')
    else:return redirect('/login')
    
@app.route('/editar_usuariof', methods=['GET','POST'])
@login_required
def editar2():    
    global sesion_ini
    if(sesion_ini==True):
        if(request.method =="GET"):
            return render_template('editar_usuariof.html')
        else: 
            id=int(request.form['id'])
            nombre = request.form['nombre']
            correo= request.form['correo']
            contraseña=request.form['contraseña']
            telefono= request.form['telefono']
            direccion= request.form['direccion']
            db=get_db()
            query26='UPDATE USUARIO SET NOMBRE =?,CORREO=?,CONTRASEÑA=?,TELEFONO=?,DIRECCION=?  WHERE ID=?'
            tupla26=(nombre,correo,contraseña,telefono,direccion,id)
            db.execute(query26,tupla26)
            db.commit()   
            return redirect('/editar_usuariof')
    else:
        return redirect('/login')
   

@app.route('/agregar_plato', methods=['GET','POST'])
@login_required
def agregar():
    global sesion_ini
    if(sesion_ini):
        if(request.method =="GET"):
            return render_template('agregar_plato.html')
        else: 
            nombre = request.form['nombre_plato']
            descripcion= request.form['descripcion']
            precio=request.form['precio']
            foto= request.form['foto']
            db=get_db()
            query27="INSERT INTO PLATO(NOMBRE,DESCRIPCION,PRECIO,FOTO) VALUES(?,?,?,?)"
            tupla27=(nombre,descripcion,precio,foto)
            db.execute(query27,tupla27)
            db.commit()   
            return redirect('/agregar_plato')
    else:
        return redirect('/login')

@app.route('/editar_plato', methods=['GET','POST'])
@login_required
def editar():    
    global sesion_ini
    if(sesion_ini):
        if(request.method =="GET"):
            return render_template('editar_plato.html')
        else: 
            id=int(request.form['id'])
            nombre = request.form['nombre_plato']
            descripcion= request.form['descripcion']
            precio=request.form['precio']
            foto= request.form['foto']
            db=get_db()
            query28='UPDATE PLATO SET NOMBRE =?,DESCRIPCION=?,PRECIO=?,FOTO=?  WHERE ID=?'
            tupla28=(nombre,descripcion,precio,foto,id)
            db.execute(query28,tupla28)
            db.commit()   
            return redirect('/editar_plato')
    else:
        return redirect('/login')
     
@app.route('/agregar_usuariof', methods=['GET','POST'])
@login_required
def agregar2():
    global sesion_ini
    if(sesion_ini):
        if(request.method =="GET"):
            return render_template('agregar_usuariof.html')
        else: 
            nombre = request.form['nombre']
            correo= request.form['correo']
            contraseña=request.form['contraseña']
            telefono= request.form['telefono']
            direccion= request.form['direccion']
            rol="usuariof"
            db=get_db()
            if not utils.isPasswordValid(contraseña):
                error = 'La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres'
                flash( error )
                return render_template('agregar_usuariof.html',error=error )

            if not utils.isEmailValid(correo):
                error = 'Correo invalido'
                flash( error )
                return render_template('agregar_usuariof.html',error=error)
            query29='SELECT ID FROM USUARIO WHERE CORREO = ?'
            tupla29=(correo,)
            encontrado=db.execute(query29,tupla29).fetchone()
            print(encontrado)
            if encontrado is not None:
                error = f"El correo {correo}  ya existe"
                flash( error )
                return render_template('agregar_usuariof.html', error=error)
            query30="INSERT INTO USUARIO(ROL,NOMBRE,CORREO,CONTRASEÑA,TELEFONO,DIRECCION) VALUES(?,?,?,?,?,?)"
            tupla30=(rol,nombre,correo,generate_password_hash(contraseña),telefono,direccion)
            db.execute(query30,tupla30)
            db.commit()
            return redirect( '/agregar_usuariof' )
    else:
        return redirect('/login')
    

@app.route('/agregarAdmin', methods=['GET','POST'])
@login_required
def agregarAdmin():
    global sesion_ini
    if(sesion_ini):
        if(request.method =="GET"):
            return render_template('agregarAdmin.html')
        else: 
            nombre = request.form['nombre']
            correo= request.form['correo']
            contraseña=request.form['contraseña']
            telefono= request.form['telefono']
            direccion= request.form['direccion']
            rol="admin"
            db=get_db()
            query31="INSERT INTO USUARIO(ROL,NOMBRE,CORREO,CONTRASEÑA,TELEFONO,DIRECCION) VALUES(?,?,?,?,?,?)"
            tupla31=(rol,nombre,correo,generate_password_hash(contraseña),telefono,direccion)
            db.executescript(query31,tupla31)
            db.commit()   
            return redirect('/agregarAdmin')
    else:
        return redirect('/login')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html') 

if __name__ == '__main__':
    app.run(debug=True)  #Opcion para activar el modo debug, para no hacerlo desde la cmd
    


