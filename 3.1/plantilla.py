# -*- coding: utf-8 -*-
import re
import web
import anydbm
from web import form
from web.contrib.template import render_mako

urls = (
	'/', 'index',
	'/logout', 'logout',
	'/informacion', 'informacion',
	'/modifica', 'modifica',
	'/fotos', 'fotos'
	)

# Para poder usar sesiones con web.py
web.config.debug = False

app = web.application(urls, globals())

email = re.compile(r'\w+@([a-z]+\.)+[a-z]+')
visa = re.compile(r'[0-9]{4}([\ \-]?)[0-9]{4}([\ \-]?)[0-9]{4}([\ \-]?)[0-9]{4}')

session = web.session.Session(app, web.session.DiskStore('sessions'))

plantillas = render_mako(
	directories=['templates'],
	input_encoding='utf-8',
	output_encoding='utf-8'
	)

#Formulario
formlogin = form.Form(
	form.Textbox ('username', form.notnull, description='Usuario'),
	form.Password ('password', form.notnull, description='Contraseña'),
	form.Button ('Login')
	)

formModifica = form.Form(
	form.Textbox('nombre', maxlength="40", description="Nombre:"),
	form.Textbox('apellidos', maxlength="50", description="Apellidos:"),
	form.Textbox('dni', maxlength="9", size="9", description="DNI:"),
	form.Textbox('correo', maxlength="50", size="15", description="Correo Electronico:"),
	form.Dropdown('dia', range(1,32), description="Dia:"),
	form.Dropdown('mes', range(1,13), description="Mes:"),
	form.Dropdown('anio', range(1940,2014), description="Anio:"),
	form.Textarea('direccion', maxlength="55", size="35", description="Direccion:"),	
	form.Password('passw', maxlength="10", size="12", description="Password:"),
	form.Password('passw2', maxlength="10", size="12", description="Repetir:"),
	form.Radio('forma_pago', ['contra reembolso', 'tarjeta visa'], description="Forma de pago:"),
	form.Textbox('numero_visa', maxlength="19", size="20", description="Numero Visa"), 
	form.Button('Aceptar', type="submit"),
	
	validators = [
    	form.Validator('El campo nombre no puede estar vacio.', lambda i: len(str(i.nombre))>0),
		form.Validator('El campo apellidos no puede estar vacio.', lambda i: len(str(i.apellidos))>0),
		form.Validator('El campo dni no puede estar vacio.', lambda i: len(str(i.dni))>0),
		form.Validator('El campo correo no puede estar vacio.', lambda i: len(str(i.correo))>0),
		form.Validator('El campo direccion no puede estar vacio.', lambda i: len(str(i.direccion))>0),
		form.Validator('El campo numero visa no puede estar vacio.', lambda i: len(str(i.numero_visa))>0),
		form.Validator('Fecha Incorrecta.', lambda x: not(
			(int(x.dia)==31 and int(x.mes)==2) or 
			(int(x.dia)==30 and int(x.mes)==2) or 
			(int(x.dia)==29 and int(x.mes)==2 and int(x.anio)%4!=0) or 
			(int(x.dia)==31 and (int(x.mes)==4 or int(x.mes)==6 or int(x.mes)==9 or int(x.mes)==11))
		)),  
		form.Validator("Formato de correo no valido.", lambda i: email.match(i.correo)),
		form.Validator("El password debe contener mas de 7 caracteres.", lambda i: len(str(i.passw))>7),
		form.Validator("El password debe contener mas de 7 caracteres.", lambda i: len(str(i.passw2))>7),
		form.Validator("El password no coindice.", lambda i: i.passw == i.passw2),
		form.Validator("Formato de visa no valido.", lambda i: visa.match(i.numero_visa))]
	)

# Funcion para el mensaje de logout, y que nos sirve para ver si esta identificado o no
def bienvenido(usuario):
	return str("Bienvenido " + str(usuario) + " (<a href='/logout'>Logout</a>)")

def guarda_visitas():
	return str("\
			<ol>\
				<li> "+ str(session.primera) + "</li>\
				<li> "+ str(session.segunda) + "</li>\
				<li> "+ str(session.tercera) + "</li>\
			</ol>\
		")

def base_datos():
	data = {}
	db = anydbm.open('db','r')
	for k, v in db.iteritems():
		data[k] = v
	db.close()
	return str("\
		<ul>\
			<li> Nombre: "+ str(data["nombre"]) + "</li>\
			<li> Apellidos: "+ str(data["apellidos"]) + "</li>\
			<li> DNI: "+ str(data["dni"]) + "</li>\
			<li> Correo: "+ str(data["correo"]) + "</li>\
			<li> Dia: "+ str(data["dia"]) + "</li>\
			<li> Mes: "+ str(data["mes"]) + "</li>\
			<li> Anio: "+ str(data["anio"]) + "</li>\
			<li> Direccion: "+ str(data["direccion"]) + "</li>\
			<li> Contrasena: "+ str(data["passw"]) + "</li>\
			<li> Verificacion contrasena: "+ str(data["passw2"]) + "</li>\
			<li> Forma de pago: "+ str(data["forma_pago"]) + "</li>\
			<li> Numero tarjeta: "+ str(data["numero_visa"]) + "</li>\
		</ul> \
		")

def modificados():
	return str("Datos modificados correctamente.")

class index:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo= "Principal", form = formulario)
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/'>Principal</a>"
			return plantillas.index(titulo= "Principal", iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

	def POST(self):
		formulario = formlogin()

		if not formulario.validates(): 
			return plantillas.index(form = formulario)
		else:
			i = web.input()
			usuario = i.username
			session.usuario = usuario
			session.primera = "<a href='/'>Principal</a>"
			session.segunda = ""
			session.tercera = ""
			return plantillas.index(titulo = "Principal", iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class informacion:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Informacion", form = formulario)
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/informacion'>Informacion</a>"
			return plantillas.index(titulo = "Informacion", iniciado = bienvenido(session.usuario), personal = base_datos(),visitas = guarda_visitas())

class modifica:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Mofifica", form = formulario)
		else:
			data = {}
			db = anydbm.open('db','r')
			for k, v in db.iteritems():
				data[k] = v
			db.close()
			formulario2 = formModifica()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/modifica'>Modificar Datos</a>"
			formulario2.nombre.value = str(data["nombre"])
			formulario2.apellidos.value = str(data["apellidos"])
			formulario2.dni.value = str(data["dni"])
			formulario2.correo.value = str(data["correo"])
			formulario2.dia.value = int(data["dia"])
			formulario2.mes.value = int(data["mes"])
			formulario2.anio.value = int(data["anio"])
			formulario2.direccion.value = str(data["direccion"])
			formulario2.passw.value = str(data["passw"])
			formulario2.passw2.value = str(data["passw2"])
			formulario2.forma_pago.value = str(data["forma_pago"])
			formulario2.numero_visa.value = str(data["numero_visa"])
			return plantillas.index(titulo = "Modificada", iniciado = bienvenido(session.usuario), form2 = formulario2, visitas = guarda_visitas())

	def POST(self):
		formulario2 = formModifica()
		if not formulario2.validates(): 
			return plantillas.index(form2 = formulario2, iniciado = bienvenido(session.usuario))
		else:
			base = web.input()
        	db = anydbm.open('db','w')
        	db["nombre"] = str(base.nombre)
        	db["apellidos"] = str(base.apellidos)
        	db["dni"] = str(base.dni)
        	db["correo"] = str(base.correo)
        	db["dia"] = str(base.dia)
        	db["mes"] = str(base.mes)
        	db["anio"] = str(base.anio)
        	db["direccion"] = str(base.direccion)
        	db["passw"] = str(base.passw)
        	db["passw2"] = str(base.passw2)
        	db["forma_pago"] = str(base.forma_pago)
        	db["numero_visa"] = str(base.numero_visa)
        	db.close()
        	return plantillas.index(titulo = "Modifica", iniciado = bienvenido(session.usuario), felicidades = modificados())

class fotos:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Fotos", form = formulario)
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/fotos'>Fotos</a>"
			return plantillas.index(titulo = "Fotos", iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class logout:
	def GET(self):
		session.kill()
		raise web.seeother('/')

if __name__ == "__main__":
	app.run()