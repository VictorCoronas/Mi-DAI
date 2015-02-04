#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import web
import anydbm
from web import form
from pymongo import MongoClient
from web.contrib.template import render_mako
import tweepy
import pymongo
import feedparser
import sys
import os.path
import urllib
import datetime
from time import time

urls = (
	'/', 'index',
	'/logout', 'logout',
	'/informacion', 'informacion',
	'/modifica', 'modifica',
	'/fotos', 'fotos',
	'/rss', 'rss',
	'/noticia', 'noticia',
	'/noticia2', 'noticia2',
	'/mapa', 'mapa',
	'/charts', 'charts',
	'/charts3d', 'charts3d',
	'/chartscom', 'chartscom',
	'/chartsregistro', 'chartsregistro',
	'/chartsmuestra','chartsmuestra',
	'/chartsjq','chartsjq',
	'/twitter', 'twitter',
	'/mapa_twitter', 'mapa_twitter'
	)

# Para poder usar sesiones con web.py
web.config.debug = False

app = web.application(urls, globals())

email = re.compile(r'\w+@([a-z]+\.)+[a-z]+')
visa = re.compile(r'[0-9]{4}([\ \-]?)[0-9]{4}([\ \-]?)[0-9]{4}([\ \-]?)[0-9]{4}')

#db =  cliente['registro']

#user = db.registros

cliente = MongoClient('mongodb://localhost:27017/')

try:
    conn=pymongo.Connection()
    print "Conexion realizada con exito"
except pymongo.errors.ConnectionFailure, e:
    print "No se puede conectar %s" %e
conn

db = conn['prueba']
collection = db.my_collection
				
contado = {"clave":"visita","index":0, "informacion":0, "mofifica":0, "rss":0, "foto":0, "mapa":0, "grafica":0, "twitter": 0, "mapstwitter":0, "insertagrafica":0, "muestragrafica":0}

collection.insert(contado)

session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'time':''})

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

formulario_mapa = form.Form (
	form.Textbox('origen', form.notnull, description='origen: '),
	form.Textbox('destino', form.notnull, description='destino: '),
	form.Button('Enviar')
	)

formulario_twitter = form.Form(
	form.Dropdown('ciudad', ['granada', 'almeria', 'cordoba','malaga','jaen','huelva','cadiz'], description="¿De que ciudad quiere ver tweets?"),
	form.Button ('Buscar')
	)

formulario_grafica_o = form.Form(
	form.Button ('Grafica Secciones')
	)

formulario_graficas = form.Form(
	form.Button ('Grafica 3D')
	)

formulario_combinada = form.Form(
	form.Button ('Grafica combinada')
	)

formulario_buscar = form.Form(
	form.Button ('Grafica combinada')
	)

formulario_charts_registro = form.Form(
	form.Textbox("nombre", form.notnull, description = 'Introduzca el nombre del grafico:'),
	form.Textbox("lunes", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia los Lunes:'),
	form.Textbox("martes", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia los Martes:'),
	form.Textbox("miercoles", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia los Miercoles:'),
	form.Textbox("jueves", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia los Jueves:'),
	form.Textbox("viernes", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia Los Viernes:'),
	form.Textbox("sabado", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia los Sabados:'),
	form.Textbox("domingo", form.notnull, description = 'Introduzca el numero de veces que lee el periodico al dia los Domingos:'),
	form.Button("Enviar")
)

formulario_nombre_charts = form.Form(
	form.Textbox("nombre", form.notnull, description = 'Introduzca el nombre de la grafica a buscar:'),
   form.Button("Enviar")
)

formulario_noticia = form.Form(
	form.Textbox ('noticia', form.notnull, description='¿Que numero de noticia deseas leer?'),
	form.Button ('Buscar'))
	
formulario_noticia2 = form.Form(
	form.Textbox ('noticia', form.notnull, description='Busque la noticia por terminos: '),
	form.Button ('Buscar'))

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
			cursor = db.my_collection.find({"clave":"visita"})
			index = cursor[0]["index"]
			index += 1
			
			db.my_collection.update({"clave":"visita"},{"$set":{"index":index}})
			db.my_collection.find_one({"clave":"visita"})
			return plantillas.index(titulo= "Principal", index = index, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

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
			cursor = db.my_collection.find({"clave":"visita"})
			mofifica = cursor[0]["mofifica"]
			mofifica += 1
			
			db.my_collection.update({"clave":"visita"},{"$set":{"mofifica":mofifica}})
			db.my_collection.find_one({"clave":"visita"})
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

class rss:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Rss", form = formulario)
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/rss'>Rss</a>"
			cursor = db.my_collection.find({"clave":"visita"})
			rsss = cursor[0]["rss"]
			rsss += 1
			
			db.my_collection.update({"clave":"visita"},{"$set":{"rss":rsss}})
			db.my_collection.find_one({"clave":"visita"})

			if session.time == '':
				t = time()
				session.time = t
			
			t2 = time()
			tiempo2 = int(t2)
			tiempo = int(session.time) + 600
			print session.time
			print tiempo2
			
			if tiempo >= tiempo2:
				web = urllib.urlretrieve('http://ep00.epimg.net/rss/elpais/portada.xml')
				f = open(web[0],'r')
				f2 = open('elpais.xml','w')
				t = time()
				session.time = t
				f2.write(f.read())
				f2.close()

			d = feedparser.parse('elpais.xml')
			rss_portada = d['feed']['title']	

			tam = len(d.entries)
			pos = 0
			rss = []
			while pos < tam:
				rss.append(d.entries[pos].title)
				pos += 1
			
			imagenes = 0
			for items in d["items"]:
				for links in items["links"]:
					if links["type"] == "image/jpeg":
						imagenes += 1
						#urllib.urlretrieve(links["href"], "static/" + str(imagenes) + ".jpg");
			
			form_noticia = formulario_noticia()
			form_noticia2 = formulario_noticia2()
			
			return plantillas.rss(titulo = "Rss", posicion = tam, imagenes = imagenes, rss_portada = rss_portada, rss = rss, form_noticia = form_noticia, form_noticia2 = form_noticia2, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class noticia:
	def POST(self):
		form_noticia = formulario_noticia()
		if not form_noticia.validates():
			return plantillas.rss(tirulo = "Rss", form_noticia = form_noticia, iniciado = bienvenido(session.usuario))
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/noticia'>Noticia</a>"

			numero = form_noticia.d.noticia
			numero_noticia = int(numero)
			numero_noticia = numero_noticia - 1
		
			
			d = feedparser.parse('elpais.xml')
			tituloss = d.entries[numero_noticia].title
			contenido = d.entries[numero_noticia].content[0].value
			fotos = d.entries[numero_noticia].enclosures[0].href
				
			return plantillas.noticia(titulo = "Noticia", titulos = tituloss, contenido = contenido, foto = fotos, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class noticia2:	
	def POST(self):
		form_noticia2 = formulario_noticia2()
		if not form_noticia2.validates():
			return plantillas.rss(titulo = "Rss", form_noticia2 = form_noticia2, iniciado = bienvenido(session.usuario))
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/noticia2'>Noticia2</a>"
			noticias = form_noticia2.d.noticia
			
			d = feedparser.parse('elpais.xml')
			
			tam = len(d.entries)
			pos = 0
			while pos < tam:
				if noticias in d.entries[pos].title:
					tituloss = d.entries[pos].title
					contenido = d.entries[pos].content[0].value
					fotos = d.entries[pos].enclosures[0].href
					return plantillas.noticia(titulo = "Noticia", titulos = tituloss, contenido = contenido, foto = fotos, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
				else:
					pos = pos + 1
			
			tituloss = 'Noticia no encontrada'
			contenido = 'Pruebe buscando otro término'
			fotos=0
			return plantillas.noticia(titulo = "Noticia", titulos = tituloss, contenido = contenido, foto = fotos, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class fotos:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Fotos", form = formulario)
		else:
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/fotos'>Fotos</a>"
			consulta = list(db.my_collection.find({"clave":"visita"}))
			cursor = db.my_collection.find({"clave":"visita"})
			foto = cursor[0]["foto"]
			foto += 1
			
			db.my_collection.update({"clave":"visita"},{"$set":{"foto":foto}})
			db.my_collection.find_one({"clave":"visita"})

			return plantillas.index(titulo = "Fotos", iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class mapa:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.mapa(titulo = "Mapa", form = formulario)
		else:
			formap = formulario_mapa()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/mapa'>Mapa</a>"
			cursor = db.my_collection.find({"clave":"visita"})
			mapa = cursor[0]["mapa"]
			mapa += 1
			
			db.my_collection.update({"clave":"visita"},{"$set":{"mapa":mapa}})
			db.my_collection.find_one({"clave":"visita"})
			return plantillas.mapa(titulo = "Mapa", form3 = formap, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
	def POST(self):
		formap = formulario_mapa()
		if not formap.validates(): 
			return plantillas.mapa(form3 = formap, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
		else:
			origen = formap.d.origen
			destino = formap.d.destino
			return plantillas.mapa2(titulo = "Mapa", origen = origen, destino = destino, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class charts:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Charts", form = formulario)
		else:
			formgrafica_o = formulario_grafica_o()
			formgrafica = formulario_graficas()
			formgrafica2 = formulario_combinada()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/charts'>Graficas</a>"
			cursor = db.my_collection.find({"clave":"visita"})
			grafica = cursor[0]["grafica"]
			grafica += 1
			index = cursor[0]["index"]
			modifica = cursor[0]["mofifica"]
			rss = cursor[0]["rss"]
			foto = cursor[0]["foto"]
			mapa = cursor[0]["mapa"]
			twitter = cursor[0]["twitter"]

			
			db.my_collection.update({"clave":"visita"},{"$set":{"grafica":grafica}})
			db.my_collection.find_one({"clave":"visita"})
			return plantillas.charts(titulo = "Graficas", formgrafica_o = formgrafica_o, formgrafica = formgrafica, formgrafica2 = formgrafica2, index = index, modifica = modifica, rss = rss, foto = foto, mapa = mapa, grafica = grafica, twitter = twitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
	def POST(self):
			formgrafica_o = formulario_grafica_o()
			formgrafica = formulario_graficas()
			formgrafica2 = formulario_combinada()
			cursor = db.my_collection.find({"clave":"visita"})
			grafica = cursor[0]["grafica"]
			index = cursor[0]["index"]
			modifica = cursor[0]["mofifica"]
			rss = cursor[0]["rss"]
			foto = cursor[0]["foto"]
			mapa = cursor[0]["mapa"]
			twitter = cursor[0]["twitter"]
			return plantillas.charts(titulo = "Graficas", formgrafica_o = formgrafica_o, formgrafica = formgrafica, formgrafica2 = formgrafica2, index = index, modifica = modifica, rss = rss, foto = foto, mapa = mapa, grafica = grafica, twitter = twitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class charts3d:
	def POST(self):
		formgrafica_o = formulario_grafica_o()
		formgrafica = formulario_graficas()
		formgrafica2 = formulario_combinada()
		cursor = db.my_collection.find({"clave":"visita"})
		grafica = cursor[0]["grafica"]
		index = cursor[0]["index"]
		modifica = cursor[0]["mofifica"]
		rss = cursor[0]["rss"]
		foto = cursor[0]["foto"]
		mapa = cursor[0]["mapa"]
		twitter = cursor[0]["twitter"]

		session.tercera = session.segunda
		session.segunda = session.primera
		session.primera = "<a href='/charts'>Graficas</a>"
		return plantillas.charts3d(titulo = "Graficas", formgrafica_o = formgrafica_o, formgrafica = formgrafica, formgrafica2 = formgrafica2, index = index, modifica = modifica, rss = rss, foto = foto, mapa = mapa, grafica = grafica, twitter = twitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class chartscom:
	def POST(self):
		formgrafica_o = formulario_grafica_o()
		formgrafica = formulario_graficas()
		formgrafica2 = formulario_combinada()
		cursor = db.my_collection.find({"clave":"visita"})
		grafica = cursor[0]["grafica"]
		index = cursor[0]["index"]
		modifica = cursor[0]["mofifica"]
		rss = cursor[0]["rss"]
		foto = cursor[0]["foto"]
		mapa = cursor[0]["mapa"]
		twitter = cursor[0]["twitter"]
		session.tercera = session.segunda
		session.segunda = session.primera
		session.primera = "<a href='/charts'>Graficas</a>"
		return plantillas.chartscom(titulo = "Graficas", formgrafica_o = formgrafica_o, formgrafica = formgrafica, formgrafica2 = formgrafica2, index = index, modifica = modifica, rss = rss, foto = foto, mapa = mapa, grafica = grafica, twitter = twitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class chartsjq:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Charts Registro", form = formulario)
		else:
			cursor = db.my_collection.find({"clave":"visita"})
			grafica = cursor[0]["grafica"]
			index = cursor[0]["index"]
			modifica = cursor[0]["mofifica"]
			rss = cursor[0]["rss"]
			foto = cursor[0]["foto"]
			mapa = cursor[0]["mapa"]
			twitter = cursor[0]["twitter"]
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/chartsjq'>JQ</a>"

			return plantillas.chartsjq(titulo = "JQ", index = index, modifica = modifica, rss = rss, foto = foto, mapa = mapa, grafica = grafica, twitter = twitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class chartsregistro:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Charts Registro", form = formulario)
		else:
			formregistro = formulario_charts_registro()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/chartsregistro'>Inserta Grafica</a>"

			return plantillas.chartsregistro(titulo = "Inserta Charts", formregistro = formregistro, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
	def POST(self):
		formregistro = formulario_charts_registro()
		if not formregistro.validates():
			return plantillas.chartsregistro(titulo = "Inserta Charts", formregistro = formregistro, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
		else:
			dias = {"nombre":formregistro.d.nombre,
					"lunes": formregistro.d.lunes,
				    "martes": formregistro.d.martes,
				    "miercoles": formregistro.d.miercoles,
				    "jueves": formregistro.d.jueves,
				    "viernes": formregistro.d.viernes,
				    "sabado": formregistro.d.sabado,
				    "domingo": formregistro.d.domingo}

			collection.insert(dias)
			consulta = list(db.my_collection.find({"nombre":formregistro.d.nombre}))
			return plantillas.chartsregistro(titulo = "Inserta Charts",consulta = consulta, iniciado = bienvenido(session.usuario), felicidades = 'Datos almacenados correctamente.')

class chartsmuestra:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Muestra Charts", form = formulario)
		else:
			formnombre = formulario_nombre_charts()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/chartsmuestra'>Muestra Charts</a>"

			return plantillas.chartsregistro(titulo = "Muestra Charts", formnombre = formnombre, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
	def POST(self):
		formnombre = formulario_nombre_charts()
		if not formnombre.validates():
			return plantillas.chartsmuestra(titulo = "Muestra Charts", formnombre = formnombre, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
		else:
			cursor = db.my_collection.find({"nombre":formnombre.d.nombre})
			lunes = cursor[0]["lunes"]
			martes = cursor[0]["martes"]
			miercoles = cursor[0]["miercoles"]
			jueves = cursor[0]["jueves"]
			viernes = cursor[0]["viernes"]
			sabado = cursor[0]["sabado"]
			domingo = cursor[0]["domingo"]

			return plantillas.chartsmuestra(titulo = "Muestra Charts", formnombre = formnombre, lunes = lunes, martes = martes, miercoles = miercoles, jueves = jueves, viernes = viernes, sabado = sabado, domingo = domingo, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class twitter:
	def GET(self):
		if 'usuario' not in session:
			formulario = formlogin()
			return plantillas.index(titulo = "Twitter", form = formulario)
		else:
			formtwitter = formulario_twitter()
			session.tercera = session.segunda
			session.segunda = session.primera
			session.primera = "<a href='/twitter'>Twitter</a>"
			cursor = db.my_collection.find({"clave":"visita"})
			twitter = cursor[0]["twitter"]
			twitter += 1
			
			db.my_collection.update({"clave":"visita"},{"$set":{"twitter":twitter}})
			db.my_collection.find_one({"clave":"visita"})
			return plantillas.twitter(titulo = "Twitter", form4 = formtwitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
	def POST(self):
		formtwitter = formulario_twitter()
		if not formtwitter.validates():
			return plantillas.twitter(form4 = formtwitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())
		else:
			ciudad = formtwitter.d.ciudad

			CONSUMER_KEY = 'YWXmBFFsIdBKCKmxyz45ZIa1x'
			CONSUMER_SECRET = 'eG1sbOivvo6qZLmoG7OZ6bAL0zSYzfWaR1qtPZkzflFtbl5V9K'
			ACCESS_KEY = '462881180-Lq6eOJTComjp7JnkCqsuDL20J5MjX3As2jay5oxv'
			ACCESS_SECRET = 'cIXdbj3kG6l0SLKX4FXDKm7fhLJxSQiAnf7wAxwazuzLe'

			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
			api = tweepy.API(auth)
			
			#tweets = api.search(q=valor, count=30)
			if ciudad == 'granada':
				tweets = api.search(geocode="37.175894,-3.59779,0.5km",count=50)

			elif ciudad == 'almeria':
				tweets = api.search(geocode="36.841528,-2.45711,0.5km",count=50)
				
			elif ciudad == 'cordoba':
				tweets = api.search(geocode="37.88931,-4.779155,0.5km",count=50)
				
			elif ciudad == 'malaga':
				tweets = api.search(geocode="36.718887,-4.419831,0.5km",count=50)
				
			elif ciudad == 'jaen':
				tweets = api.search(geocode="37.767803,-3.790772,0.5km",count=50)
				
			elif ciudad == 'huelva':
				tweets = api.search(geocode="37.261374,-6.944681,0.5km",count=50)
				
			elif ciudad == 'cadiz':
				tweets = api.search(geocode="36.52714,-6.288859,0.5km",count=50)
			
			
			tweet = []
			for result in tweets:
				tweet.append(result.text)
			return plantillas.twitter2(titulo = "Twitter", tweet=tweet, form4 = formtwitter, iniciado = bienvenido(session.usuario), visitas = guarda_visitas())

class logout:
	def GET(self):
		session.kill()
		raise web.seeother('/')

if __name__ == "__main__":
	app.run()