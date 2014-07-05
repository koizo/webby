from webby import Response

class Auth(object):


    def __init__(self, wrap_app):
        self.wrap_app = wrap_app

    def __call__(self, environ, start_response):
        
        #obter a resposta da wrap_app
        response_iter = self.wrap_app(environ, start_response)
        #analisar resposta
        response_string = ''.join(response_iter)
        print response_string
        if response_string == 'Ivan':
        	return "Pasta Privada"
        else:
        	return response_string




