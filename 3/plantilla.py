# -*- coding: utf-8 -*-
import re
import web
from web import form
from web.contrib.template import render_mako

urls = (
	'/', 'index',
	'/about.html','about'
	)

# Para poder usar sesiones con web.py
web.config.debug = False

app = web.application(urls, globals(), autoreload=True)

plantillas = render_mako(
	directories=['templates'],
	input_encoding='utf-8',
	output_encoding='utf-8'
	)

formlogin = form.Form(
	form.Textbox ('username', form.notnull, desciption='Usuario'),
	form.Password ('password', form.notnull, desciption='contraseña'),
	form.Button ('Enviar')
	)

class index:
	def GET(self):
		return plantillas.index()

class about:
	def GET(self):
		return plantillas.about()

if __name__ == '__main__':
	app.run()