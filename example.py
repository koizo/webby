from webby import Webby
from wsgiref.simple_server import make_server



app = Webby()


@app.register("/")
def ola(request):
    return "Index"

app.serve()




