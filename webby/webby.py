#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webby is a very simple micro-framework for small web applications.
Its implemented with 3 base classes: Request,Response and Webby. Its based on
wsgiref.
Webby works by registering the url paths with functions on a url_dict that will
be used when requests arrive.
A very basic example is provider in the example.py

Homepage and documentation: http://webby.koizo.net/

Copyright (c) 2014, Hugo Correia.
License: APACHE License
"""

__author__ = 'Hugo Correia'
__version__ = '0.1'
__license__ = 'APACHE License'


from wsgiref.simple_server import make_server
import urlparse
import json

#from wsgistate.memory import session
#__location__ = os.path.realpath(os.path.join(os.getcwd(), ''))

urls_dict = {}

HTTP_CODE = {
	200: 'OK',
	201: 'CREATED',
	202: 'ACCEPTED',
	400: 'BAD REQUEST',
	401: 'UNAUTHORIZED',
	403: 'FORBIDDEN',
	404: 'NOT FOUND',
	500: 'INTERNAL SERVER ERROR',
	501: 'NOT IMPLEMENTED',
}

#
# Exceptions Handling
#
class WebbyException(Exception):
    """ class for webby exception handling """
    pass

#
# Framework
#
class Request(object):
    """Request class to acess the clients request data"""

    def __init__(self, environ):
        """Recives a environ from wsgi from the request"""
        self.environ = environ

    @property
    def content_type(self):
        return self.environ['CONTENT_TYPE']

    @property
    def path(self):
        """Returns the path of the url"""
        return self.environ['PATH_INFO'].lstrip('/')

    @property
    def method(self):
        """Returns GET/POST/PUT/DELETE"""
        return self.environ['REQUEST_METHOD']

    @property
    def cookies(self):
        """Returns a wsgistate cookie"""
        cookie = self.environ['HTTP_COOKIE']
        raise NotImplementedError

    @property
    def args(self):
        """Returns the query string passed with the url"""
        return self.query_args

    @property
    def json(self):
        """Json object from request body"""
        if self.method not in ['POST', 'PUT']:
            raise AttributeError("Ilegal method type: "+self.method)

        try:
            body_size = int(self.environ['CONTENT_LENGTH'])
            return json.loads((self.environ['wsgi.input'].read(body_size)))
        except ValueError:
            return {}

    @property
    def get(self):
        """Gets a value from a variable sent by GET"""
        if environ['QUERY_STRING'] is not '':
        	self.query_args = dict(urlparse.parse_qs(environ['QUERY_STRING']))
       	else:
            self.query_args = dict()

    @property
    def remote_addr(self):
        """Remote IP from the client"""
        return self.environ['REMOTE_ADDR']

    def post(self,value):
        """Get a value from a variable sent by POST"""
        return urlparse.parse_qs(self.environ['wsgi.input'].readline().decode(),True)

    @property
    def forms(self):
        """Form data passed by POST OR PUT"""
        if self.method not in ['POST', 'PUT']:
            raise AttributeError("Ilegal method type: "+self.method)

        try:
            body_size = int(self.environ['CONTENT_LENGTH'])
            return dict(urlparse.parse_qsl(self.environ['wsgi.input'].read(body_size).decode('utf-8')))
        except ValueError:
            return None

    @property
    def files(self):
        """Files uploaded passed by POST OR PUT"""
        raise NotImplementedError

    def __repr__(self):
         return '<%s: %s %s>' % (Request, self.method, self.environ)


class Response(object):
    """Response class to be used for the resposes to the cliente"""

    status = 200
    content_type = 'text/html'

    def __init__(self,start_response):
        self.headers = {'content-type': 'text/html'}
        self.start_response = start_response


    def _status(self,statuscode):
        """Setter for status"""
        if statuscode in HTTP_CODE:
            self.status = statuscode
        else:
            raise AttributeError("Ilegal Status Code.")

    def _content_type(self,content_type):
        """Setter for content_type"""
        self.content_type = content_type


    def sendresponse(self,response):
        """Parse the response and send to the client with the correct codes"""
        self.start_response(str(self.status)+' OK', [('content-type', self.content_type)])
        #print response
        return [response]


class Webby(object):
    """Class Webby: Framework WEB"""
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        self.request     = Request(environ)
        self.response     = Response(start_response)
        print self.request
        return self.dispatch()

    def dispatch(self):
        """
        From the Request.path, gets the function to run from the urls_dict
        and responds to the client
        """
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
        """Decorator to register paths"""
        def decorator(f):
            """Saves in url_dict the Methods and the function to run from a path"""
            path = func.lstrip('/')
            if 'methods' in params:
                urls_dict[path]= {'function':f, 'request_methods': params['methods']}
            else:
                urls_dict[path]= {'function':f, 'request_methods': {"GET", "POST", 'PUT', 'DELETE'}}
            return f

        return decorator

    def parse_path(self):
        """url path parsing"""
        return self.request.environ['PATH_INFO'].lstrip('/')

    def errorhandler(self, code, function=None):
        """handling errors with Response"""
        self.response._status(code)
        html_response = HTMLErrorResponse(self.response)
        return self.response.sendresponse(html_response.html)

    def serve(self,app=None):
        """Creates a http server"""
        if app is None:
            httpd = make_server('', 8000, self)
        else:
            httpd = make_server('', 8000, app)
        print "Webby: port 8000..."
        httpd.serve_forever()

#
# Error Handling
#
class HTMLErrorResponse(object):
	""" class for http response for errors"""

	def __init__(self,response):
		self.response_body = "<html>" \
							 "<title>%s %s </title>" \
							 "<h1>%s</h1>" \
							 "<p>Webby WebServer %s" % (HTTP_CODE[response.status],response.status,HTTP_CODE[response.status],__version__)

	@property
	def html(self):
		return self.response_body
		#modify to user templating

