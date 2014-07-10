#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webby is a very simple micro-framework for small web applications.
Its implemented with 3 base classes: Request,Response and Webby. Its based on
wsgiref.
Webby works by registering the url paths with functions on a url_dict that will
be used when requests arrive.
A very basic example is provider in the example.py§
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
    301: 'REDIRECT',
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
    def __init__(self, message):
        print "WebbyException: "+message

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
        	query_args = dict(urlparse.parse_qs(environ['QUERY_STRING']))
        else:
            query_args = dict()

        return query_args

    @property
    def remote_addr(self):
        """Remote IP from the client"""
        return self.environ['REMOTE_ADDR']

    @property
    def body(self):
        """Form data passed by POST OR PUT"""
        if self.method not in ['POST', 'PUT']:
            raise AttributeError("Ilegal method type: "+self.method)

        try:
            body_size = int(self.environ['CONTENT_LENGTH'])
            return dict(urlparse.parse_qsl(self.environ['wsgi.input'].read(body_size).decode('utf-8')))
        except ValueError:
            return dict()

    @property
    def files(self):
        """Files uploaded passed by POST OR PUT"""
        raise NotImplementedError

    def __repr__(self):
         return '<%s: %s %s>' % (Request, self.method, self.environ)


class Response(object):
    """Response class to be used for the resposes to the cliente"""

    _status = 200
    _content_type = 'text/html'

    def __init__(self, start_response):
        self.headers = {'content-type': 'text/html'}
        self.start_response = start_response

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value in HTTP_CODE:
            self._status = value
        else:    
            raise AttributeError("Ilegal Status Code.")

    @property
    def content_type(self):
        """Setter for content_type"""
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        """Setter for content_type"""
        self._content_type = value

    def sendresponse(self, response):
        """Parse the response and send to the client with the correct codes"""
        if self.status== 301:
            self.start_response('301 Redirect', [('Location', self.redirect),])
            return "Redirecting to "+self.redirect

        self.start_response(str(self.status)+' '+HTTP_CODE[self.status], [('content-type', self.content_type)])
        return [response]


class Webby(object):
    """Class Webby: Framework WEB"""
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        self.request = Request(environ)
        self.response = Response(start_response)
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

        return self.errorhandler(404)

    def register(self, func, **params):
        """Decorator to register paths"""
        def decorator(f):
            """Saves in url_dict the Methods and the function to run from a path"""
            if f is None:
                raise WebbyException("Function is Invalid")

            path = func.lstrip('/')
            if 'methods' in params:
                urls_dict[path] ={'function': f, 'request_methods': params['methods']}
            else:
                urls_dict[path] ={'function': f, 'request_methods': {"GET", "POST", 'PUT', 'DELETE'}}
            return f

        return decorator

    def parse_path(self):
        """url path parsing"""
        return self.request.environ['PATH_INFO'].lstrip('/')

    def errorhandler(self, code, function=None):
        """handling errors with Response"""
        self.response.status = code
        html_response = HTMLErrorResponse(self.response)
        return self.response.sendresponse(html_response.html)


    def redirect(self, url):
        """Redirects the request to another URL. Needs to be better"""
        self.response.status = 301
        self.response.redirect = url


    def serve(self, app=None):
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
    """class for http response for errors"""

    def __init__(self,response):
        self.response_body = "<html>" \
                             "<title>%s %s </title>" \
                             "<h1>%s</h1>" \
                             "<p>Webby WebServer %s" % (HTTP_CODE[response.status],response.status,HTTP_CODE[response.status],__version__)

    @property
    def html(self):
        return self.response_body
        #modify to user templating

