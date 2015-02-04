# -*- coding: utf-8 -*-
import web
from web import form

render = web.template.render('templates/') 

urls = (
    '/', 'Index',
    '/login', 'Login',
    '/logout', 'Logout',
)

web.config.debug = False
app = web.application(urls, locals())

formlogin = form.Form(
    form.Textbox ('username', form.notnull, desciption='Usuario'),
    form.Password ('password', form.notnull, desciption='contraseña'),
    form.Button ('Enviar')
    )

session = web.session.Session(app, web.session.DiskStore('sessions'))      

class Index:
    def GET(self):
        form = formlogin()
        if session.get('logged_in', False):
            render.user(form)
            return '<h1>You are logged in</h1><a href="/logout">Logout</a>'
        return render.user(form)

class Login:
    def GET(self):
        session.logged_in = True
        raise web.seeother('/')

class Logout:
    def GET(self):
        session.logged_in = False
        raise web.seeother('/')


if __name__ == '__main__':
    app.run()