from flask import Flask, request, redirect, url_for, render_template, flash

"""
COMANDO INSTALACIÓN POR pip : python -m pip install SomePackage
"""

app = Flask(__name__)

app.secret_key = 'random string'

usuarioEnLinea = []

ciudades = []
aereolineas = []
secciones = []

salida = ''
llegada = ''
aereo = ''
dur = 0
esc = 0

vuelos = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/reservas', methods = ['GET', 'POST'])
def reservas():
    global salida, llegada, aereo, dur, esc
    ciudadesGet()
    aereoGet()

    if request.method == 'POST':
        salida = str(request.form.get('salidahtml'))
        llegada = str(request.form.get('llegadahtml'))
        aereo = str(request.form.get('aereohtml'))
        dur = int(request.form.get('tiempohtml'))
        esc = int(request.form.get('escalashtml'))
        return redirect(url_for('reservasDisp'))

    return render_template('reservas.html', ciudades = ciudades, aereolineas=aereolineas, salida = salida,
                            llegada = llegada, aereo = aereo, dur = dur, esc = esc)


@app.route('/vuelos_disponibles', methods = ['GET', 'POST'])
def reservasDisp():
    global salida, llegada, aereo, dur, esc
    salidaAux = salida[:-1]
    llegadaAux = llegada[:-1]
    print(salidaAux)
    busquedaVuelos(salidaAux,llegadaAux,aereo,dur,esc)

    if request.method == 'POST':
        escogido = request.form.get('vuelohtml')
        if usuarioEnLinea != []:
            with open('C:\\temp\\ARCHIVOS2\\reservas.txt', 'a') as myfile:
                myfile.write(usuarioEnLinea[0]+'|'+escogido+'\n')
            return redirect(url_for('home'))
        else:
            flash("Nadie ha iniciado sesión")
            return redirect(url_for('inicioSesion'))
    
    return render_template('reservasdisp.html', vuelos = vuelos)

def busquedaVuelos(salida, llegada, aereo, dur, esc):
    global vuelos
    with open('C:\\temp\\ARCHIVOS2\\datos.txt', 'r') as myfile:
        lectura = myfile.read()
        seccion = lectura.split('|')
        lineas = seccion[3].splitlines()
        contadorAux = 1
        while contadorAux < len(lineas):
            lineaAux = lineas[contadorAux]
            if lineaAux[0:2] == aereo:
                if lineaAux[8:11] == salida:
                    if lineaAux[19:22] == llegada:
                        ini = lineaAux[12:17]
                        fin = lineaAux[23:28]
                        if dur >= convertirHora(ini, fin):
                            aux = int(lineaAux[36])
                            if esc >= aux:
                                vuelos.append(lineaAux)
                                contadorAux += 1
                            else:
                                contadorAux += 1
                        else:
                            contadorAux += 1
                    else:
                        contadorAux += 1
                else:
                    contadorAux += 1
            else:
                contadorAux += 1
def convertirHora(ini,fin):
    if ini[4]=='P':
        ini = ini[0:2]
        ini = int(ini)+12
    else:
        ini = int(ini[0:2])
    if fin[4]=='P':
        fin = fin[0:2]
        fin = int(fin)+12
    else:
        fin = int(fin[0:2])

    diferencia = int(fin) - int(ini)
    return diferencia


def ciudadesGet():
    if ciudades == []:
        with open('C:\\temp\\ARCHIVOS2\\datos.txt', 'r') as myfile:
            leer = myfile.read()
            secciones = leer.split('|')
            lineas = secciones[1].splitlines()
            contadorAux = 1
            while contadorAux<len(lineas):
                ci= lineas[contadorAux][0:4]
                ciudades.append(ci)
                contadorAux += 1

def aereoGet():
    if aereolineas == []:
        with open('C:\\temp\\ARCHIVOS2\\datos.txt', 'r') as myfile:
            leer = myfile.read()
            secciones = leer.split('|')
            lineas = secciones[3].splitlines()
            contadorAux = 1
            while contadorAux<len(lineas):
                aer = lineas[contadorAux][0:2]
                if ((aer in aereolineas)==True):
                    contadorAux += 1
                    continue
                else:
                    aereolineas.append(aer)
                    contadorAux += 1

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/cerrar-sesion', methods=['GET','POST'])
def cerrarSesion():
    global usuarioEnLinea
    if usuarioEnLinea == []:
        return redirect(url_for('inicioSesion'))
    if request.method == 'POST':
        usuarioEnLinea = []
        return redirect(url_for('home'))
    return render_template('cerrar.html')
        

@app.route('/inicio-sesion', methods=['GET','POST'])
def inicioSesion():
    usuarioInp = request.form.get("Usuario",False)
    contraInp = request.form.get("Contraseña",False)
    contador = 0
    encontrado = False
    if request.method == 'POST':
        
        with open('C:\\temp\\ARCHIVOS2\\usuarios.txt', 'r') as myfile:
            leer = myfile.read()
            lineas = leer.splitlines()

            while (contador < len(lineas)) and (encontrado == False):
                datosUsuario = lineas[contador]
                div = datosUsuario.split('|')
                usuario = div[0]
                contra = div[1]
                if (usuarioInp == usuario) and (contraInp == contra):
                    usuarioEnLinea.append(usuario)
                    encontrado = True
                    return redirect(url_for('home'))
                else:
                    contador += 1
                   
    return render_template('inicioSesion.html')

@app.route('/registro', methods=['GET','POST'])
def registro():
    error = None    
    nombre = ''
    usuario = ''
    contra = ''
    confirmar =''
    if request.method == 'POST':  
        nombre = request.form.get("Nombre", False)
        usuario = request.form.get("Usuario", False)
        contra = request.form.get("Contraseña", False)
        confirmar = request.form.get("Confirmar",False)
        
        if (validarContraseña(contra, confirmar) == False)\
           or (len(nombre)==0) or (len(usuario)==0) \
           or (len(contra)==0):
            error = "No se pudo registrar, intente de nuevo."
        else:
            with open('C:\\temp\\ARCHIVOS2\\usuarios.txt', 'a') as myfile:
                myfile.write(usuario+'|'+contra+'|'+nombre+'\n')
            flash("Se registró correctamente")
            return redirect(url_for('home'))
        
    return render_template('registro.html', error = error)

def validarContraseña(a,b):
    if (a != b):
        return False
    elif (a == b):
        return True

if __name__ == '__main__':
    app.run(debug = True)
