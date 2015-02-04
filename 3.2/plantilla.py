# -*- coding: utf-8 -*-
import re
import web
import anydbm
from web import form
from pymongo import MongoClient
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

cliente = MongoClient('mongodb://localhost:27017/')

session = web.session.Session(app, web.session.DiskStore('sessions'))

plantillas = render_mako(
	directories=['templates'],
	input_encoding='utf-8',
	output_encoding='utf-8'
	)

#Formulario
formlogin = form.Form(
	form.Textbox ('usuario', form.notnull, description='Usuario'),
	form.Password ('passw', form.notnull, description='Contraseña'),
	form.Button ('Login')
	)

def carga_base():
  db = cliente['registro'] 
  user = db.registros
  data = user.find_one({"usuario": session.usuario})
  session.id = data["_id"]
  return form.Form(
	form.Textbox('nombre', maxlength="40", description="Nombre:", value=data['nombre']),
	form.Textbox('apellidos', maxlength="50", description="Apellidos:", value=data['apellidos']),
	form.Textbox('dni', maxlength="9", size="9", description="DNI:", value=data['dni']),
	form.Textbox('correo', maxlength="50", size="15", description="Correo Electronico:", value=data['correo']),
	form.Dropdown('dia', range(1,32), description="Dia:", value=int(data['dia'])),
	form.Dropdown('mes', range(1,13), description="Mes:", value=int(data['mes'])),
	form.Dropdown('anio', range(1940,2014), description="Anio:", value=int(data['anio'])),
	form.Textarea('direccion', maxlength="55", size="35", description="Direccion:", value=data['direccion']),	
	form.Password('passw', maxlength="10", size="12", description="Password:", value=data['passw']),
	form.Password('passw2', maxlength="10", size="12", description="Password2:", value=data['passw']),
	form.Radio('forma_pago', ['contra reembolso', 'tarjeta visa'], description="Forma de pago:", value=data['forma_pago']),
	form.Textbox('numero_visa', maxlength="19", size="20", description="Numero Visa", value=data['numero_visa']), 
	form.Button('Modificar', type="submit"),
	
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
	return str("Bienvenido " + str(session.usuario) + " (<a href='/logout'>Logout</a>)")

def guarda_visitas():
	return str("\
			<ol>\
				<li> "+ str(session.primera) + "</li>\
				<li> "+ str(session.segunda) + "</li>\
				<li> "+ str(session.tercera) + "</li>\
			</ol>\
		")

def base_datos(data):
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
			db = cliente['registro']
			user = db.registros
			data = user.find_one({'$and': [{"usuario": i.usuario, "passw": i.passw}]})
			if not data:
				return plantillas.index(form = formulario)
			else:
				session.usuario = i.usuario
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
			db = cliente['registro']
			user = db.registros
			datos = user.find_one({"usuario": session.usuario})
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/informacion'>Informacion</a>"
			return plantillas.index(titulo = "Informacion", iniciado = bienvenido(session.usuario), personal = base_datos(datos),visitas = guarda_visitas())

class modifica:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Mofifica", form = formulario)
		else:
			carga = carga_base()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/modifica'>Modificar Datos</a>"
			return plantillas.index(titulo = "Modificada", iniciado = bienvenido(session.usuario), form2 = carga, visitas = guarda_visitas())
	def POST(self):
		carga = carga_base()
		if not carga.validates(): 
			return plantillas.index(form2 = carga, iniciado = bienvenido(session.usuario))
		else:
			actualiza = web.input()
			db = cliente['registro']
			user = db.registros
			data = {"nombre": str(actualiza.nombre), "apellidos": str(actualiza.apellidos), "dni": str(actualiza.dni), "correo": str(actualiza.correo), "dia": str(actualiza.dia), "mes": str(actualiza.mes), "anio": str(actualiza.anio), "direccion": str(actualiza.direccion), "passw": str(actualiza.passw), "forma_pago": str(actualiza.forma_pago), "numero_visa": str(actualiza.numero_visa)}
			user.update(
				{'_id': session.id},
				{'$set': data},
				upsert=False)
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