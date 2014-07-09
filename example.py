from webby import Webby

app = Webby()

@app.register("/",methods={"GET","POST"})
def ola(request):
    return "Index"

app.serve()




