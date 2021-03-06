# -*- coding: utf-8 -*-

import re
import web
import anydbm
from web import form

render = web.template.render('templates/')  #tenemos acceso a todos los html de esta carpeta

urls = (
    '/', 'formular' 
)

app = web.application(urls, globals())

# 404
def notfound():
	return web.notfound("No se encuentra la página que estas buscando")

app.notfound = notfound

email = re.compile(r'\w+@([a-z]+\.)+[a-z]+')
visa = re.compile(r'[0-9]{4}([\ \-]?)[0-9]{4}([\ \-]?)[0-9]{4}([\ \-]?)[0-9]{4}')

myform = form.Form( 
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
    form.Checkbox('check',
		form.Validator("Debe aceptar las clausulas.", lambda i: "check" not in i), description="Acepto las clausulas"), 
	form.Button('Aceptar'),
	
	
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


class formular: 
    def GET(self): 
		form = myform() # creamos una copia del formulario para evitar acceder al mismo formulario a la vez
		return render.formtest(form)
    def POST(self): 
        form = myform() 
        if not form.validates():# recoge todas las variables y construye una estructura de datos, también comprueba si se cumplen los validadores que me haya creado
        	return render.formtest(form)
        else:
        	base = web.input()
        	db = anydbm.open('db','c')
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
        	return "Felicidades %s %s te has registrado satisfactoriamente." % (form.d.nombre, form['apellidos'].value)

if __name__=="__main__":
    app.run()