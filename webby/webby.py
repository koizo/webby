from wsgiref.simple_server import make_server
from .mappings import HTTP_CODE
import os
import urlparse

#__location__ = os.path.realpath(os.path.join(os.getcwd(), ''))

urls_dict = {}

class Request(object):

	#para nao esquecer
	method = None
	mimetype = None
	form = None
	args = None
	path = None
	environ = None
	cookie = None
	content_type = None

	def __init__(self, environ):
		self.environ = environ

		if environ['QUERY_STRING'] is not '':
			self.args = urlparse.parse_qs(environ['QUERY_STRING'])
		else:
			self.args = {}

		self.method = environ['REQUEST_METHOD']
		self.path = environ['PATH_INFO']
		#self.form = environ['']
		self.cookie = environ['HTTP_COOKIE']
		self.content_type = environ['CONTENT_TYPE']

	def get(self,value):
		#so uma variavel por cada tipo
		if value in self.args:
			return self.args[value][0]
		else:
			return ""

	def post(self,value):
		return None


class Response(object):

	status = 200
	content_type = 'text/html'

	def __init__(self,start_response):
		self.headers = {'content-type': 'text/html'}
		self.returnquote = start_response

	def sendresponse(self,response):
		self.returnquote(str(self.status)+' OK', [('content-type', self.content_type)])
		return [response]


class Webby:

	def __init__(self):
		pass
		
	def __call__(self, environ, start_response):

		self.request 	= Request(environ)
		self.response 	= Response(start_response)

		return self.dispatch_request()

	def dispatch_request(self):

		path = self.parse_path()
		#media suport
		if path in urls_dict:
			if self.request.method in urls_dict[path]['request_methods']:
				return self.response.sendresponse(urls_dict[path]['function'](self.request))
			else:
				return self.errorhandler(404)
		else:
			return self.errorhandler(404)

	def register(self, func, **params):
		def decorator(f):
			path = func.lstrip('/')
			if 'methods' in params:
				urls_dict[path]= {'function':f,'request_methods': params['methods']}
			else:
				urls_dict[path]= {'function':f,'request_methods':{"GET","POST",'PUT','DELETE'}}
			return f	

		return decorator

	def parse_path(self):
		return self.request.environ['PATH_INFO'].lstrip('/')

	def errorhandler(self, code, function=None):
		self.response.status = code
		return self.response.sendresponse(HTTP_CODE[code])
		
	def serve(self,app=None):
		if app is None:
			httpd = make_server('', 8000, self)
		else:
			httpd = make_server('', 8000, app)
		print "Webby: port 8000..."
		httpd.serve_forever()

