import web


urls = ( "/", "index")
render = web.template.render('templates/')
class index:
    def GET(self):
        i = web.input(name=None)
        return render.index(i.name)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
