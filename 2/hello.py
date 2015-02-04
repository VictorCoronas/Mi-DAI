import web

from web import form

render = web.template.render('templates/')  #tenemos acceso a todos los html de esta carpeta      

urls = (
    '/hello/(.*)', 'hello', #nombre de la clase que crearemos despues
    '/lol/(.*)', 'lol', #nombre de la clase que crearemos despues
    '/formulario/', 'formulario' #nombre de la clase que crearemos despues
    )

def notfound():
	return web.notfound("Lo sentimos no furula la pagina.")


app = web.application(urls, globals())
app.notfound = notfound

myform = form.Form(
	form.Textbox("Nombre"),
	form.Textbox("Numero",
		form.notnull,
		form.regexp('\d+', 'Deben de ser digitos.'),
		form.Validator('Debe de ser 9 o mas digitos', lambda x:int(x)>=9)),
	form.Textarea('Comentario'),
	form.Checkbox('Acepto los terminos.'),
	form.Dropdown('Espanol', ['Basico', 'Normal', 'Experto'])
)

class formulario:
	def GET(self):
		form = myform()
		return render.formtest(form)
	def POST(self):
		form = myform()
		if not form.validates():
			return render.formtest(form)
		else:
			return "great success! Nombre: %s, Numero: %s" % (form.d.Nombre, form['Numero'].value)

class hello:  # es la clase Hello que se declara antes en la url      
    def GET(self, name): # name= una varible que esta en el archivo htmal,le pasa el nombre al archivo html y ve si tiene o no nombre
        return render.hola(name) #devuelve el hello com  nombre o sin nombre del html
        						 #hola seria el archivo html dentro de 
class lol:  # es la clase Hello que se declara antes en la url      
    def GET(self, name): # name= una varible que esta en el archivo htmal,le pasa el nombre al archivo html y ve si tiene o no nombre
        return render.lol(name) #devuelve el hello com  nombre o sin nombre del html
        						 #hola seria el archivo html dentro de templates
if __name__ == "__main__":
	app.run()